#! /bin/bash
set -ev

if [ "${TRAVIS_PULL_REQUEST}" = "false" ]; then
    pip install -r requirements.txt
    make html

    if [ "$TRAVIS_BRANCH" = "master" ]; then
        git clone --branch gh-pages https://${GH_TOKEN}@github.com/$TRAVIS_REPO_SLUG.git ./OUTPUT
        OUTDIR=./OUTPUT
    else
        git clone --branch gh-pages https://${GH_TOKEN}@github.com/Crunch-io/crunchy.git ./OUTPUT
        mkdir -p ./OUTPUT/apidocs
        OUTDIR=./OUTPUT/apidocs
    fi

    rsync -av build/html/ $OUTDIR

    cd $OUTDIR

    echo "Letting git know about all the changes..."
    git add -A

    echo "Committing them... even if there were 0 changes"
    git commit -m "Updating apidocs site (build ${TRAVIS_BUILD_NUMBER})" --allow-empty

    echo "Pushing to Github!"
    git push --quiet origin gh-pages || true
fi
