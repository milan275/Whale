import shutil,json
from pathlib import Path
from crypt import crypt_engine



class vault:

    def __init__(self,name="my_vault",password="",src="./test",dest="./vaults",ex_dest="./temp",backup="./backups",chunk_size=32000000,fake=None):

        self.name=name
        self.password=password
        self.src=src
        self.dest=dest
        self.ex_dest=ex_dest
        self.backup = backup
        self.chunk_size = chunk_size
        self.fake_vault = vault(name="fake_"+name,src=fake,ex_dest=self.ex_dest) if(password) else None

    @staticmethod
    def get_folder(source):
        return sorted(Path(source).iterdir(),key=lambda x:x.name)

    def create(self):
        ce=crypt_engine(self.password,self.chunk_size)
        def add_folder(source,offset=0):
            header = {}
            tot=0
            folder = self.get_folder(source)
            for item in folder:
                if item.is_dir() :
                    header[item.name]=add_folder(item,offset+tot)
                    tot+=header[item.name]["size"]
            
                elif item.is_file():
                    size = ce.size(item.stat().st_size)
                    header[item.name]={"size":size,"offset":offset+tot}
                    tot+=size

            return {"content":header,"size":tot,"offset":offset}


        header = json.dumps({self.name:add_folder(self.src)}).encode("utf-8")
        header_size = ce.size(len(header))
        


        def add_content(source,stream):
            folder = self.get_folder(source)
            for item in folder:
                if item.is_dir() :
                    add_content(item,stream)
                    
                elif item.is_file():
                    size = item.stat().st_size
                    with open(item,"rb") as file:
                        for i in range(0,size,self.chunk_size):
                            chunk = ce.encrypt(file.read(self.chunk_size))
                            stream.write(chunk)
                

        with open(Path(self.dest)/f"{self.name}.whale","wb") as stream:
            stream.write(ce.salt)
            stream.write(header_size.to_bytes(4,byteorder="big"))
            stream.write(ce.encrypt(header))
            add_content(self.src,stream)


        #backup
        backup_dir = Path(self.backup)
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(self.dest) / f"{self.name}.whale", backup_dir / f"{self.name}.whale")

        if(self.fake_vault):
            self.fake_vault.create() 

    def extract(self):
        
        with open(Path(self.dest)/f"{self.name}.whale","rb") as whale:
            salt = whale.read(16)
            ce=crypt_engine(self.password,self.chunk_size,salt)
            true_cs = ce.size(self.chunk_size)
            header_size = int.from_bytes(whale.read(4),byteorder="big")
            header = ce.decrypt(whale.read(header_size))
            
            if header == ce.fake_mess:
                self.fake_vault.extract()
                return 0
            header = json.loads(header)
            def get(header,dest):
                dest=Path(dest)
                if dest.exists() and dest.is_dir():
                    shutil.rmtree(dest)
                dest.mkdir(parents=True,exist_ok=True)
                
                header = header["content"]
                for item in header:
                    if "content" in header[item]:
                        get(header[item],dest/item)
                    else:
                        size = header[item]["size"]
                        with open(dest/item,"wb") as file:
                            for i in range(0,size//true_cs):
                                file.write(ce.decrypt(whale.read(true_cs)))
                            file.write(ce.decrypt(whale.read(size%true_cs)))
            
            get(header[self.name],self.ex_dest)
            return 1

    

            
















