<p align="center"><h1 align="center">FASTAPI-TEMPLATE</h1></p>
<p align="center">
	<em><code>❯ FastApi template</code></em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/mart337i/fastapi-template?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/mart337i/fastapi-template?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/mart337i/fastapi-template?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/mart337i/fastapi-template?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

<code>❯ A Fastapi template</code>

---

##  Features

<code>❯ Disable and enable routes on the fly</code> <br>
<code>❯ Auto load config files</code> <br>
<code>❯ Load all the modules in the `addons` file automatic </code> <br>


---

##  Project Structure

```sh
└── fastapi-template/
    ├── .github
    │   └── workflows
    ├── Dockerfile
    ├── LICENSE
    ├── README.Docker.md
    ├── README.md
    ├── alembic
    │   ├── README
    │   ├── env.py
    │   └── script.py.mako
    ├── alembic.ini
    ├── app
    │   ├── __init__.py
    │   ├── addons
    │   ├── base
    │   └── main.py
    ├── docker-stack.yaml
    ├── gunicorn
    ├── poetry.lock
    └── pyproject.toml
```

---
##  Getting Started

###  Prerequisites

Before getting started with fastapi-template, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Package Manager:** Poetry
- **Container Runtime:** Docker


###  Installation

Install fastapi-template using one of the following methods:

**Build from source:**

1. Clone the fastapi-template repository:
```sh
❯ git clone https://github.com/mart337i/fastapi-template
```

2. Navigate to the project directory:
```sh
❯ cd fastapi-template
```

3. Install the project dependencies:


**Using `poetry`** &nbsp; [<img align="center" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" />](https://python-poetry.org/)

```sh
❯ poetry install
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker compose -f docker-stack.yaml up --build
```




###  Usage
Run fastapi-template using the following command:

**Using `Fastapi`** &nbsp; [<img align="center" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" />](https://python-poetry.org/)

```sh
❯ fastapi dev app/main.py 
```


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker compose -f docker-stack.yaml up --build
```


###  Testing
Run the test suite using the following command:

**Using `poetry`** &nbsp; [<img align="center" src="https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json" />](https://python-poetry.org/)

```sh
❯ poetry run pytest -v --import-mode=importlib
```


---
##  Project Roadmap

- [X] **`Task 1`**: <strike>Enable and disable modules on the fly</strike>

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/mart337i/fastapi-template/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/mart337i/fastapi-template/issues)**: Submit bugs found or log feature requests for the `fastapi-template` project.
- **💡 [Submit Pull Requests](https://github.com/mart337i/fastapi-template/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/mart337i/fastapi-template
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

---

##  License

This project is protected under the MIT License. For more details.

---

##  Acknowledgments
Thank you to the builders of the following: 

- Fastapi
- SQLMODEL
- python-dotenv
- pytest

You made this hobby project possible! 

---
