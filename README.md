<!-- PROJECT LOGO -->
<br />
<div align="center">
  <!-- <a href="https://github.com/github_username/repo_name">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a> -->

<h1 align="center">Crypto Option Dashboard</h1>

  <p align="center">
    Dashboard to view the past performance of Option on Deribit
    <br />
    <a href="https://github.com/marcNY/crypto_option_dashboard"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/marcNY/crypto_option_dashboard">View Demo</a>
    ·
    <a href="https://github.com/marcNY/crypto_option_dashboard/issues">Report Bug</a>
    ·
    <a href="https://github.com/marcNY/crypto_option_dashboard/issues">Request Feature</a>
  </p>
</div>


<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get the code running on your computer


### Prerequisites

To use this code you will need to have Python 3.x as well as a virtualenv.
1. You can check the version of Python that you have using:
```sh
python --version
```
if you do not have Python 3.x you can install it using [https://brew.sh/](Homebrew) with the following command:
```sh
 brew install python
```

2. Install virtualenv, this will allow us to have a self contained installation:
```sh
pip install virtualenv
virtualenv --version
```

### Installation

1. Get a free API Key at [https://test.deribit.com/](https://test.deribit.com/).
Make sure that your IP has been whitelisted.

2. Clone the repo
```sh
git clone https://github.com/marcNY/crypto_option_dashboard.git
```

3. In the main folder create a file `credentials.json` and store your credentials in the following format:
```
{
    "client_id" : "uEDh4567",
    "client_secret" : "nsjV6YYIhsjkshfaiuefhiuhwfeirhfewiiYexdDh5Bg"
}
```

4. Start a virtual environment
```sh 
virtualenv venv
source venv/bin/activate
```
5. Install the dependancies
```sh 
pip install -r requirements.txt
```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

You can interact with this code base in two ways:
1) Use the demo.ipynb Jupyter notebook to get a good grasp of the code and logic
2) Enter 'streamlit run src/option_dashboard.py' in the Terminal to launch the webapp.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#top">back to top</a>)</p>

