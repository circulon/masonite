<p align="center">
  <img src="https://raw.githubusercontent.com/masonitedev/masonite/5.0/.github/logo/masonite-mark.svg" width="160px">
  <h1 align="center">Masonite</h1>
</p>
<p align="center">
  <img alt="GitHub Workflow Status" src="https://img.shields.io/github/actions/workflow/status/masonitedev/masonite/pythonapp.yml">

  <img alt="GitHub release (latest by date including pre-releases)" src="https://img.shields.io/github/v/release/masonitedev/masonite?include_prereleases">
  <img src="https://img.shields.io/github/license/masonitedev/masonite.svg" alt="License">
  <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

## In Memory of Joseph Mancuso

Masonite was created by [Joseph "Joe" Mancuso](https://github.com/josephmancuso), who sadly passed away in November 2025.

Joe built Masonite from the ground up and poured years of work, care and enthusiasm into the framework and its community. Everything you see here exists because of him. We will continue developing and maintaining this project in his memory, keeping alive the developer-first spirit he gave it.

Thank you for everything, Joe. ❤️

## About Masonite

Stop using old frameworks with just a few confusing features. Masonite is the developer focused dev tool with all the features you need for the rapid development you deserve. Masonite is perfect for beginners getting their first web app deployed or advanced developers and businesses that need to reach for the full fleet of features available. A short list of the available features are:

* Mail support for sending emails quickly.
* Queue support to speed your application up by sending jobs to run on a queue or asynchronously.
* Notifications for sending notifications to your users simply and effectively.
* Task scheduling to run your jobs on a schedule (like everyday at midnight) so you can set and forget your tasks.
* Events you can listen for to execute listeners that perform your tasks when certain events happen in your app.
* A BEAUTIFUL Active Record style ORM called Masonite ORM. Amazingness at your fingertips.
* Many more features you need which you can find in the docs!

## Learning Masonite

New to Masonite? Read the [Official Documentation](https://docs.masonite.dev).
Masonite strives to have extremely clear documentation 😃. It would be wise to go through the tutorials there.
If you find any discrepencies or anything that doesn't make sense, please open an issue and we will get it cleared up!

## Getting Started Quickly

If you have a working Python 3.10–3.13 installation then getting started is as quick as typing

```bash
pip install masonite-framework
masonite new blog
```

The `masonite new` wizard guides you through creating your application — pick a stack (full-stack or API), a frontend preset, a database — then it creates a virtual environment, installs the dependencies, generates your application key, initializes a git repository and offers to start the development server right away.

Prefer no questions? Every step is also a flag:

```bash
masonite new blog --api --db=postgres --no-input
```

> `project start` keeps working as an alias of `masonite new` for existing tutorials and docs.

## Upgrading from 4.x (legacy) to 5.x

Masonite has moved to the [masonitedev](https://github.com/masonitedev) organization and the PyPI package has been renamed from `masonite` to `masonite-framework`.

> [!IMPORTANT]
> The legacy `MasoniteFramework/masonite` repository and the old `masonite` PyPI package (4.x and earlier) are **deprecated and will no longer receive updates or security fixes**. All development continues here. If you are running Masonite 4.x you should upgrade to 5.x from this repository.

1. Uninstall the legacy package and install the new one:

   ```bash
   pip uninstall masonite
   pip install "masonite-framework>=5,<6"
   ```

2. Imports are unchanged — you still `import masonite` / `from masonite import ...`. The `project` and `craft` commands work the same way.
3. Python 3.10–3.13 is now required (3.8/3.9 were dropped as they reached end of life).
4. Masonite ORM 3.x and Pendulum 3.x are now required. If your app parses dates directly with Pendulum, review the [Pendulum 3 changes](https://pendulum.eustace.io/blog/announcing-pendulum-3-0-0.html) (parsing is stricter). If you use `pendulum.set_test_now()` in your tests, replace it with `pendulum.travel_to()` or use the built-in `self.fakeTime()` helper.
5. Masonite ORM is now published as [`masonite-framework-orm`](https://pypi.org/project/masonite-framework-orm/) (replacing `masonite-orm`). It is installed automatically, but update your own requirement pins if you declare it directly — imports are unchanged (`from masoniteorm...`).
6. New in 5.0: a full logging system with `terminal`, `single`, `daily`, `stack`, `syslog` and `slack` drivers, configured in `config/logging.py` and available through the `Log` facade. Unhandled exceptions are logged automatically with their traceback. See the [Logging documentation](https://docs.masonite.dev/features/logging).
7. The repository now lives at https://github.com/masonitedev/masonite and the documentation at https://docs.masonite.dev — update your git remotes, issues and links:

   ```bash
   git remote set-url origin https://github.com/masonitedev/masonite.git
   ```

## Contributing

Contributing to Masonite is simple:

- Read the [Contributing Guide](https://github.com/masonitedev/masonite/blob/5.0/CONTRIBUTING.md) to learn how to contribute to the core source code development of the project.
- Open an [issue](https://github.com/masonitedev/masonite/issues) or a [pull request](https://github.com/masonitedev/masonite/pulls) to ask questions, report bugs or propose changes.

## Core Maintainers

- [Joseph Mancuso](https://github.com/josephmancuso) (Creator — in memoriam)
- [Samuel Girardin](https://github.com/girardinsamuel)
- [Marlysson Silva](https://github.com/Marlysson)
- [Eduardo Aguad](https://github.com/eaguad1337)

## Logo

With the move to masonite.dev, Masonite adopted a new brand: the Great Pyramid mark. The original logo from Joe's era remains part of the project's history.

| Legacy (2017–2025) | New (2026–) |
|:---:|:---:|
| <img src="https://raw.githubusercontent.com/masonitedev/masonite/5.0/.github/logo/masonite-logo-legacy.png" width="120" alt="Legacy Masonite logo"> | <img src="https://raw.githubusercontent.com/masonitedev/masonite/5.0/.github/logo/masonite-mark.svg" width="120" alt="New Masonite logo — the Great Pyramid mark"> |

## Security Vulnerabilities

If you discover a security vulnerability within Masonite please read the [Security Policy](./SECURITY.md). All security vulnerabilities will be promptly addressed.

## License

The Masonite framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).
