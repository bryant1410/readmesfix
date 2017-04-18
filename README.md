# Fix GitHub's Markdown headings

Because I'm tired of running into broken READMEs!

GitHub [changed the way ATX headers are parsed in Markdown files](https://gist.github.com/vmarkovtsev/59cd7349d41cf804b9a8775388e681f8).
This caused many repos' READMEs to have their headings suddenly broken,
and albeit time have passed, many are still broken.

[vmarkovtsev created a dataset](https://gist.github.com/vmarkovtsev/59cd7349d41cf804b9a8775388e681f8)
([CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/))
containing the repos with more than 50 stars that contain READMEs broken
in this way. So I created this script to iterate through the list and
create a PR to fix each of them.

## Set up

**Caution: this is an automated script to create Pull Requests. Please
be cautious to avoid creating spam with it.**

The script works on Python 3.6+. To install its dependencies:

```bash
pip install -r requirements.txt
```

To run it, you first need to configure a [Personal Access
Token](https://github.com/settings/tokens) with repo:public_repo scope
to be able to fork projects and to create pull requests. Then:

```bash
export GITHUB_ACCESS_TOKEN=<YOUR ACCESS TOKEN>
./readmesfix.py
```

It will start processing each repo in the file (one by line) by cloning
it, finding its Markdown files, checking if they should be fixed,
forking them and creating a pull request. **Take into account [GitHub
API rate limiting](https://developer.github.com/v3/#rate-limiting), so
avoid overwhelming it by making the script much faster.**

To select a different dataset than `top_broken.tsv`:

```
./readmesfix.py --dataset dataset_file
```
