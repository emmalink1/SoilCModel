# .cshrc 
# John R. Makosky
# Tue Sep 16 11:29:21 CDT 1997 

# load modules here

# module load 


umask 077       # -- private, only you have access to your files
# umask 022     # -- anyone can read and execute your files
# umask 027     # -- only members of your group can read/execute your files

if ($?prompt) then		# interactive session 

   # set prompt = "`hostname` % "  # uncomment if you use csh

   # add your aliases here
   alias rm rm -i
   alias mv mv -i
   alias cp cp -i
   # alias ls ls -CF		   # uncomment if you use csh
   alias t telnet
   alias r rsh
   alias s ssh

else				# not an interactive login 

   unset noclobber

endif

