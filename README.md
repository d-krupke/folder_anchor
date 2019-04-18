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

```json

{"anchor": [{"name": "my_anchor"}, {"name": "alternative_name"}], 
"auto_link_to": [{"anchor": "some_other_anchor", "subdir": "create_a_subdir_with_this_name"},
                 {"anchor":  "yet_another_anchor", "name": "name_this_link_different", 
                 "file": "dont_link_to_the_folder_but_to_this_file"}],
"name": "default_name_of_link"}
```