MCNP Syntax Highlighting
========================

This is the latest iteration of the MCNP Notepad++ User-Defined Language (as of 6/16/2021).
To apply this to your copy of Notepad++ (NPP), download MCNP_Formatting_v1.4.xml and 
move it to the following location:

"\Users\<username>\AppData\Roaming\Notepad++\userDefineLangs"

(NOTE: If you are having trouble locating the AppData folder on a Windows computer, 
 try typing %AppData% in the search bar at the bottom-left corner of your screen.)

If you have not used a UDL before, then all you should see in the userDefineLangs folder
is a file called "markdown._preinstalled.udl". Once MCNP_Formatting_v1.4.xml is in this
folder, it should appear in NPP near the bottom of the Language tab as "MCNP".



The MCNP_Enhanced_UDL.py script is used to add a couple of extra features to the UDL 
that could not be done natively in NPP. To use it, you must first install the 
PythonScript plugin for NPP with the Plugins Admin tool under the Plugins tab of
NPP. Once installed, you must add the python script to the following location:

"Program Files/Notepad++/plugins/PythonScript/scripts"

(NOTE: You may need administrative privileges to make changes to this folder.)



After both files are in the correct locations, you must:
- Open/write the MCNP input deck in NPP
- Apply the MCNP UDL from the Languages dropdown menu
- In the Plugins dropdown, select Python Script
- In Scripts, click MCNP_Enhanced_UDL
	
Now, your MCNP input deck should be properly color-coded!
