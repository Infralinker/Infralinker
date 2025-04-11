"""
======================= START OF LICENSE NOTICE =======================
Copyright (C) 2022 by Abdellah ALAOUI ISMAILI. 
All rights reserved.
THIS FILE IS PART OF THE INFRALINKER PROJECT,
AND IS RELEASED UNDER THE "PROPRIETARY SOFTWARE LICENSE".
FILE THAT SHOULD HAVE BEEN INCLUDED AS PART OF THIS SOFTWARE.
======================== END OF LICENSE NOTICE ========================
Primary Author: Abdellah ALAOUI ISMAILI
"""

import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()