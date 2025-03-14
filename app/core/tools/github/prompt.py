# flake8: noqa
GET_ISSUE_PROMPT = """
This tool will fetch the title, body, and comment thread of a specific issue. **VERY IMPORTANT**: You must specify the issue number as an integer.
"""

COMMENT_ON_ISSUE_PROMPT = """
This tool is useful when you need to comment on a GitHub issue. Simply pass in the issue number and the comment you would like to make. Please use this sparingly as we don't want to clutter the comment threads. **VERY IMPORTANT**: Your input to this tool MUST strictly follow these rules:

- First you must specify the issue number as an integer
- Then you must place two newlines
- Then you must specify your comment
"""

CREATE_FILE_PROMPT = """
This tool is a wrapper for the GitHub API, useful when you need to create a file in a GitHub repository. **VERY IMPORTANT**: Your input to this tool MUST strictly follow these rules:

- First you must specify which file to create by passing a full file path (**IMPORTANT**: the path must not start with a slash)
- Then you must specify the contents of the file

For example, if you would like to create a file called /test/test.txt with contents "test contents", you would pass in the following string:

test/test.txt

test contents
"""

READ_FILE_PROMPT = """
This tool is a wrapper for the GitHub API, useful when you need to read the contents of a file in a GitHub repository. Simply pass in the full file path of the file you would like to read. **IMPORTANT**: the path must not start with a slash
"""

UPDATE_FILE_PROMPT = """
This tool is a wrapper for the GitHub API, useful when you need to update the contents of a file in a GitHub repository. **VERY IMPORTANT**: Your input to this tool MUST strictly follow these rules:

- First you must specify which file to modify by passing a full file path (**IMPORTANT**: the path must not start with a slash)
- Then you must specify the old contents which you would like to replace wrapped in OLD <<<< and >>>> OLD
- Then you must specify the new contents which you would like to replace the old contents with wrapped in NEW <<<< and >>>> NEW

For example, if you would like to replace the contents of the file /test/test.txt from "old contents" to "new contents", you would pass in the following string:

test/test.txt

OLD <<<<
old contents
>>>> OLD
NEW <<<<
new contents
>>>> NEW
"""

DELETE_FILE_PROMPT = """
This tool is a wrapper for the GitHub API, useful when you need to delete a file in a GitHub repository. Simply pass in the full file path of the file you would like to delete. **IMPORTANT**: the path must not start with a slash
"""