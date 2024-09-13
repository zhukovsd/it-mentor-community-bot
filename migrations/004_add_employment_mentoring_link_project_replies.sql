UPDATE "Add_project_replies"
SET message = message || '\n \- [Ментороство по трудоустройству](https://telegra.ph/Mentorstvo-po-trudoustrojstvu-06-08) \- сопровождение до оффера'
WHERE project_name = 'cloud-file-storage' OR project_name = 'task-tracker';
