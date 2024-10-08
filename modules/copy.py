import paramiko
import scp
from scp import SCPClient
import os
from datetime import datetime
from logging_config import configure_logging
import logging

def copy(client, params, host_info):
    src = params.get('src')
    dest = params.get('dest')
    backup = params.get('backup', False)

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    address = host_info.get('ssh_address')

    configure_logging()

    logging.info(dt_string + " host=" + address + " op=copy src=" + src +  " dest=" + dest + " backup=" + str(backup))

    # Vérifier si src est un fichier ou un dossier
    if os.path.isfile(src):
        # Copier un fichier
        try:
            if backup:
                # Ajouter un suffixe au nom du fichier pour la sauvegarde
                backup_dest = dest + '.backup'
                scp = SCPClient(client.get_transport())
                scp.get(dest, backup_dest)
                scp.close()

            # Copier le nouveau fichier
            scp = SCPClient(client.get_transport())
            scp.put(src, dest)
            scp.close()
            logging.info(dt_string + " host=" + address + " op=copy status=CHANGED")
        except Exception as e:
            # "e" contient le fichier défectueuse
            logging.info("COPY : failed")
    elif os.path.isdir(src):
        # Copier un dossier (récursivement)
        try:
            if backup:
                # Ajouter un suffixe au nom du dossier pour la sauvegarde
                backup_dest = os.path.join(dest, os.path.basename(src)) + '.backup'
                scp = SCPClient(client.get_transport())
                scp.get(dest, backup_dest)
                scp.close()

            # Copier le nouveau dossier
            scp = SCPClient(client.get_transport())
            scp.put(src, recursive=True, remote_path=dest)
            scp.close()
            logging.info("Folder copied: {src} -> {dest}")
        except Exception as e:
            logging.info("Error copying folder: {e}")
    else:
        logging.info("Source path is invalid or does not exist: {src}")
