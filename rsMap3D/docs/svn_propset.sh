# run this script to make sure all SVN properties are set to enable displaying
# of html pages
find build -name *.html | xargs svn propset svn:mime-type text/html
find build -name *.png  | xargs svn propset svn:mime-type application/octet-stream
find build -name *.jpg  | xargs svn propset svn:mime-type application/octet-stream
find build -name *.gif  | xargs svn propset svn:mime-type application/octet-stream
find build -name *.js   | xargs svn propset svn:mime-type text/javascript
find build -name *.css  | xargs svn propset svn:mime-type text/css