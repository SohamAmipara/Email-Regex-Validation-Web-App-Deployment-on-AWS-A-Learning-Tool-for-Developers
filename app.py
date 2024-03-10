from flask import Flask, render_template, request
import re
import dns.resolver

app = Flask(__name__)

def find_regex_matches(test_string, regex):
    # Find all matches of the regex in the test string
    matches = [(match.group(), match.start(), match.end()) for match in re.finditer(regex, test_string)]
    return matches

def validate_email(email):
    # Regular expression pattern for validating email syntax
    email_pattern = re.compile(r'^[\w\.-]+@[a-zA-Z0-9\.-]+\.[a-zA-Z]{2,}$')

    # Check if the email matches the pattern
    if not re.match(email_pattern, email):
        return False, "Invalid email syntax"

    # Split the email to get the domain
    _, domain = email.split('@')

    try:
        # Query the DNS records for the domain
        dns.resolver.resolve(domain, 'MX')
    except dns.resolver.NXDOMAIN:
        # If no DNS records found for the domain, it does not exist
        return False, "Email domain does not exist"
    except dns.resolver.NoAnswer:
        # If there are no MX (Mail Exchange) records, it does not support email
        return False, "Domain does not support email"
    except Exception as e:
        # Other errors like DNS query failure
        return False, f"Error: {str(e)}"
    
    # If everything is valid, return True
    return True, "Email is valid"

@app.route('/', methods=['GET', 'POST'])
def index():
    matches = []
    error = None

    if request.method == 'POST':
        if 'test_string' in request.form and 'regex' in request.form:
            # Regex finder form submitted
            test_string = request.form['test_string']
            regex = request.form['regex']
            matches = find_regex_matches(test_string, regex)
        elif 'email' in request.form:
            # Email validation form submitted
            email = request.form['email']
            is_valid, message = validate_email(email)
            if not is_valid:
                error = message
            else:
                error = "Email is valid"

    return render_template('index.html', matches=matches, error=error)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
