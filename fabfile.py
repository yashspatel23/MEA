from fabpolish import polish, sniff, local, info


@sniff(severity='critical', timing='fast')
def find_merge_conflict_leftovers():
    """
    Avoid merge conflicts
    """
    info('Finding merge conflict leftovers...')
    return local("! git grep -P '^(<|=|>){7}(?![<=>])'")


@sniff(severity='major', timing='fast')
def run_test():
    info('Running tests...')
    return local(
        'nose2 --config conf/nose2.cfg'
    )


@sniff(severity='major', timing='slow')
def check_pep8_styles():
    """
    Run pep8 python coding standard check
    """
    info('Running style check...')
    return local(
        "git ls-files | "
        "awk '/^healthscoop\/.*\.py$/ {print $1}' | "
        "awk '!/^healthscoop\/manage/' | "
        "xargs pycodestyle --config=conf/pycodestyle"
    )


@sniff(severity='major', timing='slow')
def run_pyflakes():
    """
    Run pyflakes
    """
    info('Running static code analysis...')
    return local(
        "git ls-files | "
        "awk '/^healthscoop\/.*\.py$/ {print $1}' | "
        "awk '!/^healthscoop\/manage/' | "
        "xargs pyflakes"
    )


if __name__ == "__main__":
    polish()
