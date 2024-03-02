import os
from app import app, db
from app.models import User, Survey, Day, Task
from datetime import datetime, timedelta
import random

#----------------------------------------
# launch
#----------------------------------------

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='localhost', port=port)




