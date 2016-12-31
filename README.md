<img src="https://raw.githubusercontent.com/johnroper100/pep8online/master/static/img/logo.png" width="50%">

Pep8Online
==========

This is a web service for Python pep8 requirements checking.

[pep8online.com](http://pep8online.com) -- Use it.

How To Run:
-----------

To download and run Pep8Online, first clone the repository:

```git clone https://github.com/Bryukh/pep8online.git```

```cd pep8online```

Then install the required packages:

```pip install -r requirements.txt```

Next try to start:

```python main.py```

If you get an error when you try to start:

```pip uninstall bson```

```pip uninstall pymongo```

```pip install pymongo```

Otherwise, open `127.0.0.1:5000` in your browser and you should see the application.

TODO:
-----
* Github URL Checking:
Save code or result as txt and pdf
inline highlight error in code