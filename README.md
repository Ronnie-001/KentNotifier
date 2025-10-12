# Notification-System
A notification system that notifies students from the University of Kent on changes to the time table, their next lecture/class etc. Rather than having to go back and forth through their timtable any updates, KentNotifier takes these updates/changes for the academic term allowing them to be displayed/viewed in one place.

# Architecture of Project
<img width="3006" height="1392" alt="image" src="https://github.com/user-attachments/assets/487fa393-928c-4078-b95a-81082365a078" />

# Current Endpoints
## Login Service:
- `/login-service/auth/v1/signup`: Users sign up for the service.
- `login-serive/auth/v1/signin`: Users sign into the service, recieving a JWT.
## Scraping Service:
- `/scraping-service/v1/get-login-details`: User's provide thier details for KentVision; automation of login so their timetable can be webscraped.
- `/scraping-service/v1/webscrape-timetable` (*IN PROGRESS*): The scraping service will periodically webscrape KentVision to detect any changes to the user's timetable throughout the term. 
