"""Start Project Command."""

from .NewCommand import NewCommand


class ProjectCommand(NewCommand):
    """
    Creates a new Masonite project (alias of `new`)

    start
        {target? : Path of your Masonite project}
        {--api : Scaffold an API-ready project}
        {--preset= : Frontend preset to use (tailwind, bootstrap, vue, react, none)}
        {--db= : Database driver to configure (sqlite, mysql, postgres)}
        {--no-venv : Do not create a virtual environment or install dependencies}
        {--no-git : Do not initialize a git repository}
        {--no-serve : Do not offer to start the development server}
        {--no-input : Do not ask any interactive question and use defaults}
        {--f|--force : Craft the project even if the target directory is not empty}
        {--repo= : Craft the project from a custom repository instead of the bundled skeleton}
        {--b|--branch=False : Specify which branch you would like to install when using --repo}
        {--r|--release=False : Specify which version you would like to install when using --repo}
        {--p|--provider=github : Repository provider to use with --repo (github, gitlab)}
    """

    # The behavior is inherited from NewCommand so `project start` and
    # `project new` cannot drift apart.
