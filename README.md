The Function Through Which the API Can Be Tested Is Given Below OR You Can Run send_req.py


    def send_post_request():
    
        url = "https://knowwize-aman-assesment.onrender.com"
       
        pdf_file_path = "Python Notes.pdf"
        
        data = {
            "num_questions": "20",
            "difficulty": "medium",
            "types": "MCQ , True/False and Fill in The Blanks",
        }
        
        files = {"pdf_file": ("file.pdf", open(pdf_file_path, "rb"), "application/pdf")}
        try:
            response = requests.post(url, data=data, files=files)
    
            if response.status_code == 200:
                print("Response from server:", response.text)
            else:
                print("Error:", response.status_code)
        except Exception as e:
            print("Error sending POST request:", e)
