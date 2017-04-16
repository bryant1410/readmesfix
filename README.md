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
