class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/sicp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False   
    # Carpeta donde se almacenarán los archivos    
    UPLOAD_FOLDER = 'uploads'  
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'} 