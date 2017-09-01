#! /bin/bash
set -ev

if [ "${TRAVIS_PULL_REQUEST}" = "false" ]; then
    bundle install
    rake build

    if [ "$TRAVIS_BRANCH" = "master" ]; then
        git clone --branch gh-pages https://${GH_TOKEN}@github.com/$TRAVIS_REPO_SLUG.git ./OUTPUT
        cd OUTPUT
    else
        git clone --branch gh-pages https://${GH_TOKEN}@github.com/Crunch-io/crunchy.git ./OUTPUT
        cd OUTPUT
        mkdir -p apidocs
        mv ../build .
        cd apidocs
    fi

    rm -rf fonts
    rm -rf javascripts
    rm -rf images
    rm -rf stylesheets
    rm -rf examples
    mv ../build/* .
    git add fonts
    git add javascripts
    git add images
    git add stylesheets
    git add examples
    git add index.html
    echo "Committing them..."
    git commit -m "Updating apidocs site (build ${TRAVIS_BUILD_NUMBER})" || true
    echo "Push!"
    git push --quiet origin gh-pages || true
fi
