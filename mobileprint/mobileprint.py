#!/usr/bin/env python3
# encoding: utf-8
"""
http://robertwdempsey.com/python3-email-with-attachments-using-gmail/
python_3_email_with_attachment.py
Created by Robert Dempsey on 12/6/14.
Copyright (c) 2014 Robert Dempsey. Use at your own peril.

This script works with Python 3.x

NOTE: replace values in ALL CAPS with your own values
"""
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from automator.automator import Automator
from automator.automator import Constants


import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '
VERBOSE = True

class EmailProperty(object):

    def __init__(self, id, pw, recipients, composed=None, server='mail.aalto.fi'):
        self.id = id
        self.pw = pw
        self.recipients = recipients
        self.composed = composed
        self.server = server
        if VERBOSE:
            self.__repr__()

    def __repr__(self):
        print("Your account info:")
        lines = ["id: {:s}".format(self.id), "recipients: {:s}".format(self.recipients[0]), "server: {:s}".format(self.server)]
        for l in lines:
            print("\t" + l)
        print()

class MobilePrint(object):
    def __init__(self, emailProperty):
        self.emailProperty = emailProperty

    def remove_ignored_items_and_dir(self, file_names):
        print("Constants.ignored", Constants.ignored)
        return [
            i for i in file_names
            if not os.path.isdir(i)                     # Remove directories
            and os.path.basename(i).lower() not in Constants.ignored # Ignore unnecessaries
        ]



    def get_file_names_in_dir(self, basepath=None):
        this_script_name = os.path.basename(__file__)
        print("this_script_name", this_script_name)
        print("__file__", __file__)
        if not basepath:
            basepath = os.path.dirname(os.path.abspath(__file__))
            print("basepath", basepath)
            # basepath = Automator.get_base_path(os.path.abspath(this_script_name))

        print("basepath", basepath)
        all_file_names = os.listdir(basepath)
        all_file_names.remove(this_script_name)
        all_file_names = [os.path.join(basepath, n)  for n in all_file_names]
        return self.remove_ignored_items_and_dir(all_file_names)

    def move_file_to_printed(self, original_path):
        import shutil
        basepath = os.path.dirname(original_path)
        basename = os.path.basename(original_path)
        printed_path = os.path.join(basepath, "printed", basename)
        shutil.move(original_path, printed_path)

    def send_email(self):
        ep = self.emailProperty
        try:
            with smtplib.SMTP(ep.server, 587) as s:
                s.ehlo()
                s.starttls()
                s.ehlo()
                s.login(ep.id, ep.pw)
                s.sendmail(ep.id, ep.recipients, ep.composed)
                s.close()
            print("Email sent!")
        except:
            print("Unable to send the email. Error: ", sys.exc_info()[0])
            raise


    def get_outer(self):
        # Create the enclosing (email) message
        outer = MIMEMultipart()
        outer['Subject'] = 'EMAIL SUBJECT'
        outer['To'] = COMMASPACE.join(self.emailProperty.recipients)
        outer['From'] = self.emailProperty.id
        outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
        return outer

    def run(self):
        # List of attachments
        attachments = self.get_file_names_in_dir()
        print("You have {:d} files".format(len(attachments)))
        for i in attachments:
            print(i)

        # Add the attachments to the message
        for file_path in attachments:
            try:
                with open(file_path, 'rb') as fp:
                    msg = MIMEBase('application', "octet-stream")
                    msg.set_payload(fp.read())
                encoders.encode_base64(msg)
                msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                outer = self.get_outer()
                outer.attach(msg)

            except IsADirectoryError as e:
                print(e)
            except:
                import sys
                print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
                raise
            else:
                composed = outer.as_string()
                self.emailProperty.composed = composed
                self.send_email()
                self.move_file_to_printed(file_path)



if __name__ == '__main__':
    automator = Automator(target_file_path=__file__)
    id = automator.secret["id"]
    pw = automator.secret["pw"]
    recipients = ['mobileprint@aalto.fi']
    ep = EmailProperty(id, pw, recipients)
    mp = MobilePrint(ep)
    mp.run()
    # print(get_file_names_in_dir())
