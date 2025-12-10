---
description: Setup and run the CodeMentorHub project
---

1. Install dependencies
```bash
pip install -r requirements.txt
```

2. Navigate to the inner directory where manage.py is located
```bash
cd mentorhub
```

3. Apply migrations
```bash
python manage.py migrate
```

4. Run the development server
```bash
python manage.py runserver
```
