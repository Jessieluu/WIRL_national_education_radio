echo "Star uwsgi."
kill $(ps aux |grep 'NationalEducationRadio/uwsgi.ini'|awk '{print $2}')
uwsgi --ini /var/www/EBCStation/Flask/NationalEducationRadio/uwsgi.ini&
echo "Done!"
