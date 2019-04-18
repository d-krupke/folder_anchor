# folder_anchor
A tool for automatically creating symbolic links.

I found myself in the situation that my working folders and files where distributed
around multiple repositories, cloud folders, etc. which makes it hard to find the files
you are looking for. For some time, I ordered everything by subject and sometimes used 
symbolic links. However, due to the vast amount of projects and tasks, a continuous
reordering is necessary (which makes links bad). Further, projects and tasks are
often not strictly separated which makes the subject based approach hard.
Symbolic links are great to have a folder/file at multiple places but they are hard
to maintain in a continuously evolving folder hierarchy. Thus, I
started to develop *folder_anchor* which uses json files to describe
the relationship between folders. More specifically to create named 'anchors'
a folder can automatically be linked to. For example a Powerpoint folder on OneDrive
for Project1 can automatically be linked to /Subjects/Area1/Project1/Powerpoint just by
saying, that this should be a Powerpoint-folder in the Project1 folder.
The tool will automatically scan through the directories and add or update
the symbolic links to match the description.


Anchors and link requests are defined in json files with the name '.folder_anchor.json'
in the corresponding directory. Such a link can look
as follows:
```json
{"anchor": [{"name": "my_anchor"}, {"name": "alternative_name"}], 
"make_part_of": [{"anchor": "some_other_anchor", "subdir": "create_a_subdir_with_this_name"},
                 {"anchor":  "yet_another_anchor", "name": "name_this_link_differently", 
                 "file": "dont_link_to_the_folder_but_to_this_file"}],
"name": "default_name_of_link"}
```

## Usage

```
usage: folder_anchor.py [-h] [-a,--anchor ANCHOR_NAME]
                        [-t,--make_part_of ANCHOR_NAME] [--subdir ./PATH]
                        [--name NAME] [--file ./FILE] [--scan PATH]
                        [-l,--list_anchors PATH]

folder_anchor is a tool for automaticallycreating symbolic links based on
localjson configuration files. See https://github.com/d-krupke/folder_anchor
for more.

optional arguments:
  -h, --help            show this help message and exit
  -a,--anchor ANCHOR_NAME
                        Create anchor
  -t,--make_part_of ANCHOR_NAME
                        Link to anchor
  --subdir ./PATH       Creates a subdir at the corresponding anchor
  --name NAME           Name of the link (if different from folder name)
  --file ./FILE         Don't like to the folder but this file.
  --scan PATH           Scans the directory and adds missing symbolic links.
  -l,--list_anchors PATH
                        Lists all anchors

```

### Creating an anchor

An anchor is a folder that one can push symbolic links to.
For example it makes sense to create an anchor for a project folder.
Now you can have a repository in your repository folder and can tell it to create a link
to it in the anchor's, i.e. project's, folder.
Or you could create a 'latex' anchor that automatically gets a latex template folder 
linked to.

```
folder_anchor.py -a my_project
```
creates an anchor named "my_project" for the current folder.
This means it creates the file `.folder_anchor.json` with the content
```json
{"anchor": [{"name": "my_project"}]}
```
We can have multiple anchors on the same folder.
Calling
`folder_anchor.py -a latex_project`
 would modify the file to
 ```json
{"anchor": [{"name": "my_project"}, {"name": "latex_project"}]}
```

### Linking to an anchor

Assume you have a folder with latex templates and you want to create a
link named 'latex_templates' in every folder that has the anchor 'latex_project'.
For this you execute in your template folder
```
folder_anchor.py --make_part_of latex_project --name latex_templates
```
This creates the file
```json
{"make_part_of": [{"anchor": "latex_project", "name": "latex_templates"}]}
``` 

Note that `--name` is optional (default is the original folder name).
If you want to put all templates in a subdirectory 'templates' you can add the
parameter `--subdir templates`.
Same as for anchors, you can add multiple such auto-links.
If you want to link a specific file in this directory, you can use the parameter `--file`.


### Creating the links

If you call `python3 folder_anchor.py -s .`, it scans all the folders in the current directory
and creates the symbolic links specified in the `.folder_anchor.json` files.
This can take a few seconds if you have a lot of folders.

## Design Decisions

### Why not allow regular expressions?

It is useful to link some folder (for example templates) to all projects
of a specific kind. However, since it is possible for a project folder to
have multiple anchor names, there is no need for this. Just add a corresponding
additional anchor to all the corresponding projects. There is also no harm
in overlapping definitions if they have the same result (the tool will 
automatically detect this).

### Does the tool overwrite any files with a wrong configuration?

No, the tool never deletes any files or folders. This also means you
have to take care of removing broken links. This is possible with
`find -L $MY_DIRECTORY -type l -exec rm -- {} +`.
When creating new symbolic links, only broken links are allowed to be overwritten.
Otherwise, a warning is printed.


### Is there a dry run option?

Yes, simply add the parameter `--dry` to get the changes printed without actually performing them.