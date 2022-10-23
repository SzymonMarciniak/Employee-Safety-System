# RUN 

# 1. Create virtual environment  *optional*
    conda create -n 'name' python=3.9.7

Remember that you need to use python in 3.9.7 version

# 2. Install dependencties 
```python 
pip install -r requirements.txt
```
If you use windows 10/11 you must also install: 

```python 
pip install pywin32==304
```
# 3. Install large files from releases
In release everything is described: https://github.com/SzymonMarciniak/Employee-Safety-System/releases

# 4. Start SQL 
Create sql table: 
```python 
CREATE DATABASE "employee_safety_system";
```
Or import .sql file 


# 5. Run application 
    python3 main.py
    
## License
[MIT](https://choosealicense.com/licenses/mit/)
