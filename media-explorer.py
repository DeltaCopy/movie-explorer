import sys
import os
import requests
import re
import datetime
import json
import urllib

from PyQt5.QtWebEngineWidgets import *

from PIL import Image

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import QSize, QDateTime, QUrl, Qt
from PyQt5.QtWidgets import QMenu, QAction, QVBoxLayout, QDateTimeEdit, QDialogButtonBox, QTextEdit, QMessageBox, QPushButton, QWidget, QLabel

qtCreatorFile_1 = "client.ui"  # Enter file here.
the_movie_db_api_search = "https://api.themoviedb.org/3/search/movie?include_adult=true&page=1&language=en-US&api_key=${api_key}&query={}"
the_movie_db_api = "https://api.themoviedb.org/3"
the_movie_db_api_key = "${api_key}"
the_movie_db_poster_orig = "https://image.tmdb.org/t/p/original"
the_movie_db_poster_w500 = "https://image.tmdb.org/t/p/w500"

cache_data_file = os.path.curdir + '/.cache/data.json' 

youtube_embed_link = "https://www.youtube.com/embed/"
#https://image.tmdb.org/t/p/original/AtsgWhDnHTq68L0lLsUrCnM7TjG.jpg


#https://www.youtube.com/watch?v=IwOW3WyV3wM


'''
import urllib

url = 'http://example.com/image.png'    
data = urllib.urlopen(url).read()
pixmap = QPixmap()
pixmap.loadFromData(data)
icon = QIcon(pixmap)
'''


class MovieData():
    def __init__(self,id,filename,title,releaseDate,description,posterPath,popularity,runtime,tagline,genre,trailer):
        self.id = id
        self.filename = filename
        self.title = title
        self.releaseDate = releaseDate
        self.description = description
        self.posterPath = posterPath
        self.popularity = popularity
        self.runtime = runtime
        self.tagline = tagline
        self.genre = genre
        self.trailer = trailer



Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile_1)

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setFixedSize(960, 910)
        self.setupUi(self)

        self.action_Open.triggered.connect(self.openFileBrowser)
        self.action_Exit.triggered.connect(self.close)

        self.pushButton_trailer.clicked.connect(self.loadTrailer)

        self.action_About.triggered.connect(self.openDialog)

        self.lineEdit_movie_title.setReadOnly(True)
        self.lineEdit_movie_title.setMaximumWidth(850)
        self.lineEdit_movie_genre.setReadOnly(True)
        self.lineEdit_movie_genre.setMaximumWidth(850)
        self.lineEdit_movie_runtime.setReadOnly(True)
        self.lineEdit_movie_runtime.setMaximumWidth(850)
        self.lineEdit_movie_popularity.setReadOnly(True)
        self.lineEdit_movie_popularity.setMaximumWidth(850)
        self.lineEdit_movie_tag.setReadOnly(True)
        self.lineEdit_movie_tag.setMaximumWidth(850)
        self.textEdit_movie_overview.setReadOnly(True)
        self.textEdit_movie_overview.setLineWrapMode(QTextEdit.WidgetWidth)
        self.textEdit_movie_overview.setWordWrapMode(
            QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.textEdit_movie_overview.setMaximumWidth(850)
        self.lineEdit_release_date.setReadOnly(True)
        self.lineEdit_release_date.setMaximumWidth(850)
        self.pushButton_trailer.setEnabled(False)

        self.createDir()

    def loadTrailer(self):
    
        trailer_metadata = self.getYouTubeVideoFromFile(self.listWidget.selectedItems()[0].text().strip())

        if(trailer_metadata is not None):
            
            self.button = QPushButton("Close")
            self.buttonBox = QDialogButtonBox()
            self.buttonBox.addButton(self.button,QDialogButtonBox.ActionRole)

            webEngineView = QWebEngineView()
            webEngineView.load(QUrl(trailer_metadata['trailer_url']))

            webEngineView.show()
            
            qdlg = QtWidgets.QDialog()
            qdlg.setWindowFlags(Qt.WindowCloseButtonHint)
            qdlg.setWindowTitle('Trailer - ' + trailer_metadata['title'])
            qdlg.setFixedSize(1000,1000)
            layout = QVBoxLayout()
            self.button.clicked.connect(qdlg.close)
            layout.addWidget(self.buttonBox)
            layout.addWidget(webEngineView)

            # Set dialog layout
            qdlg.setLayout(layout)
            qdlg.showFullScreen()
            
            qdlg.exec_()
        

    @staticmethod
    def getYouTubeVideoFromFile(filename):
        metadata = {}
        for x in json.load(open(cache_data_file))['movies']:
            if(x['filename'] == filename):
                metadata['trailer_url'] =  x['trailer']
                metadata['title'] = x['title']

                return metadata
            

    def openDialog(self):
        popup = QMessageBox(QMessageBox.Information,
                                         "About",
                                         "",
                                         
                                          QMessageBox.Ok,
                                          self)

        
        popup.setStyleSheet("QLabel{min-width:250 px}");
        
        label = QLabel(popup)
        label.setOpenExternalLinks(True)

        label.setText( "Media Explorer, is powered by " + '<a href="https://themoviedb.org"> <b>themoviedb</b> </a>')
        label.move(60,5)
       
        popup.show()

    def createDir(self):
        if (not os.path.exists(os.path.curdir + '/.cache')):
            os.mkdir(os.path.curdir + "/.cache")
            
        
        if(not os.path.exists(cache_data_file)):
            open(cache_data_file,"a").close()

            

    def actionClicked(self, action):
        print(action)

        try:
            print(action.text())
        except AttributeError as e:
            print(e)

        try:
            print(action.data())
        except AttributeError as e:
            print(e)

    def openFileBrowser(self):
        #options = QtWidgets.QFileDialog.Options()
        options = QtWidgets.QFileDialog.DontUseNativeDialog

        dirName = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Directory",options=options)
        if dirName:
            print(dirName)
            if (os.path.exists(dirName)):
                self.setWindowTitle("Media Browser - " + dirName)
                self.listWidget.clear()
                files = os.listdir(dirName)
                for f in files:
                    if ('.mkv' in f):
                        fil = f.replace('.mkv',
                                        '').replace('-', '').strip().replace(
                                            '  ', ' ')

                        self.listWidget.addItem(fil)
                self.listWidget.itemSelectionChanged.connect(self.displayItem)

    def displayItem(self):
        headers = {
            "User-agent": "python-movie-client",
            "Content-Type": "application/json"
        }

        if (len(self.listWidget.selectedItems()) > 0):
            print(self.listWidget.selectedItems()[0].text())

            movieDetails = self.getMovieInfo(
                self.listWidget.selectedItems()[0].text().strip())

            if (movieDetails is not None):
                self.lineEdit_movie_title.setText(movieDetails['title'])
                self.lineEdit_movie_runtime.setText(
                    str(movieDetails['runtime']) + "m")
                self.textEdit_movie_overview.setText(
                    movieDetails['description'].strip())
                self.lineEdit_movie_tag.setText(movieDetails['tagline'])
                self.lineEdit_release_date.setText(movieDetails['releaseDate'])
                self.lineEdit_movie_popularity.setText(
                    str(movieDetails['popularity']))

                self.lineEdit_movie_genre.setText(movieDetails['genre'])

                if (not os.path.exists(
                        os.path.curdir + "/.cache/" +
                        movieDetails["title"].replace(' ', '').strip() +
                        ".png")):
                    file = open(
                        os.path.curdir + "/.cache/" +
                        movieDetails["title"].replace(' ', '').strip() +
                        ".jpg", 'wb')
                    file.write(
                        requests.get(movieDetails['poster_path']).content)
                    file.close()

                    img = Image.open(
                        os.path.curdir + "/.cache/" +
                        movieDetails["title"].replace(' ', '').strip() +
                        ".jpg")
                    img.save(os.path.curdir + "/.cache/" +
                             movieDetails["title"].replace(' ', '').strip() +
                             ".png")
                    os.remove(os.path.curdir + "/.cache/" +
                              movieDetails["title"].replace(' ', '').strip() +
                              ".jpg")

                pixmap = QtGui.QPixmap(
                    os.path.curdir + "/.cache/" +
                    movieDetails["title"].replace(' ', '').strip() + ".png")

                pixmap4 = pixmap.scaled(431, 571,
                                        QtCore.Qt.KeepAspectRatioByExpanding,
                                        QtCore.Qt.SmoothTransformation)

                self.label.setPixmap(pixmap4)
                self.label.resize(pixmap4.width(), pixmap4.height())
                self.pushButton_trailer.setEnabled(True)


    def getMovieInfo(self, filename):
        #tmdb_session_id = getTMDBSessionId()

        searchKeySeasonEp = "S[0-9]*E[0-9]*"
        searchKeyYear = ".*([1-3][0-9]{3})"
        tvShowName = ""
        movieName = ""
        match = ""
        found = False
        print("Filename = " + filename)

        season = None
        episode = None

        season = re.search("S[0-9]*", filename)
        episode = re.search("E[0-9]*", filename)

        if (season and episode and 'S' in season[0] and 'E' in episode[0]):
            return None
        else:
            if ("." in filename):
                for x in filename.split("."):

                    matches = re.findall(searchKeyYear, x, flags=re.IGNORECASE)

                    if (len(matches) > 0):
                        break
                    else:
                        movieName += x + " "
            else:

                for x in filename.split(" "):
                    print(x)
                    matches = re.findall(searchKeyYear, x, flags=re.IGNORECASE)

                    if (len(matches) > 0):
                        break
                    else:
                        movieName += x + " "

            movieName = movieName.strip()


            if (len(movieName) > 0):
                
                
                
                cached_data = open(cache_data_file).readlines()

                if(len(cached_data) == 0):
                    movieDetails = self.getMovieDetails(filename,movieName)
                    with open(cache_data_file,"w") as f:
                        f.writelines('{"movies": [')
                        json.dump(movieDetails,f,ensure_ascii=False)
                        f.writelines(']}')
                    f.close()

                    return movieDetails

                


                else:
                    # convert json file into str
                    #cached_data_str = str(json.load(open(cache_data_file))).replace(']',',').strip().replace('\'','\"')


                    cached_movies={}

                    for x in json.load(open(cache_data_file))['movies']:
                        cached_movies[x['filename']] = MovieData(x['id'],x['filename'],x['title'],x['releaseDate'],x['description'],x['poster_path'],x['popularity'],x['runtime'],x['tagline'],x['genre'],x['trailer'])

                    
                    
                    
                    if(filename not in cached_movies.keys()):
                        
                        movieDetails = self.getMovieDetails(filename,movieName)

                       
                        
                     
                        index = 0
                        cached_len = len(cached_movies)
                        with open(cache_data_file,"w") as f:
                            #json.dump(json.dumps(json.loads(cached_data_str)),f,ensure_ascii=False)
                            if(index == 0):
                                f.writelines('{"movies": [')
                                json.dump(movieDetails,f,ensure_ascii=False)
                                #f.writelines(']}')
                                f.writelines(',')
                            for x in cached_movies:
                                f.writelines('{')
                                f.writelines('"id" : ' + '"{}'.format(cached_movies[x].id) + '",')
                                f.writelines('"filename" : ' + '"' + str(cached_movies[x].filename) + '",')
                                f.writelines('"title" : ' + '"' + str(cached_movies[x].title) + '",')
                                f.writelines('"releaseDate" : ' + '"' + str(cached_movies[x].releaseDate) + '",')
                                f.writelines('"description" :' + '"' + str(cached_movies[x].description) + '",')
                                f.writelines('"poster_path" : ' + '"' + str(cached_movies[x].posterPath) + '",')
                                f.writelines('"popularity" : ' + '"{}'.format(cached_movies[x].popularity) + '",')
                                f.writelines('"runtime" : ' + '"{}'.format(cached_movies[x].runtime) + '",')
                                f.writelines('"tagline" : ' + '"' + str(cached_movies[x].tagline) + '",')
                                f.writelines('"genre" : ' + '"' + str(cached_movies[x].genre) + '",')
                                f.writelines('"trailer" : '  + '"'+ str(cached_movies[x].trailer) + '"')
                                index +=1
                                if(index == cached_len):
                                    f.writelines('}')
                                else:
                                    f.writelines('},')

                            #f.write(json.dumps(cached_movies))
                            f.writelines(']}')
                            #f.writelines('}')
                        f.close()
                        
                        return movieDetails
                    else:
                        # use cache to pull movie data
                        print('using cache file')

                        for x in json.load(open(cache_data_file))['movies']:
                            if(x['filename'] == filename):
                                return x

            else:
                print("[TMDB] error.")
                print(response.text)
                sys.exit(1)

    @staticmethod
    def getMovieDetails(filename,movieName):
        headers = {"Content-Type": "application/json"}
        print(the_movie_db_api_search.format(movieName.replace(' ','%20')))

        response = requests.get(the_movie_db_api_search.format(movieName.strip().replace(' ', '%20')),headers=headers)

        movieDetails = {}
        movieDetails['id'] = None
        if (response.status_code == 200):

            print(movieName.strip().replace(':', '').replace(',', '').replace('!','').replace('-','').strip().upper())

            for x in response.json()['results']:

                print(x['original_title'].strip().replace(':', '').replace(',', '').replace(
                        '!',
                        '').replace('-','').strip().upper())
            
                if (x['original_title'].strip().replace(':', '').replace(',', '').replace(
                        '!',
                        '').replace('-','').strip().upper() == movieName.replace(':', '').replace(',', '').replace(
                        '!',
                        '').replace('-','').strip().upper() or len(response.json()['results']) == 1):

                    movieDetails['id'] = x['id']
                    break
            

            if (movieDetails['id']):
                response = requests.get(
                    the_movie_db_api +
                    "/movie/{}".format(movieDetails['id']) +
                    "?include_adult=true&page=1&language=en-US&api_key=d95b10bc7e817c8a5f02d041698a608d",
                    headers=headers)

                #print(the_movie_db_api + "/movie/{}".format(movieDetails['id'])+"?include_adult=true&page=1&language=en-US&api_key=d95b10bc7e817c8a5f02d041698a608d")

                movieDetails['filename'] = filename
                movieDetails["title"] = response.json()['title'].replace(
                    ':', '').replace('-','')
                movieDetails['releaseDate'] = response.json(
                )['release_date']
                movieDetails['description'] = response.json()['overview'].replace('-','').replace('\"','\'').strip()
                movieDetails[
                    'poster_path'] = the_movie_db_poster_orig + response.json(
                    )['poster_path']
                movieDetails['popularity'] = response.json()['popularity']
                movieDetails['runtime'] = response.json()['runtime']
                movieDetails['tagline'] = response.json()['tagline']

                gen = response.json()['genres']
                genres = ""

                for g in gen:
                    genres += g['name'] + " "
                movieDetails['genre'] = genres

                movieDetails['genre'] = movieDetails['genre'].strip()

                #get trailer
                response = requests.get(
                    the_movie_db_api +
                    "/movie/{}/videos".format(movieDetails['id']) +
                    "?include_adult=true&page=1&language=en-US&api_key=d95b10bc7e817c8a5f02d041698a608d",
                    headers=headers)
                
                for x in response.json()['results']:
                    if(x['type'] == 'Trailer' and 'Official Trailer' in x['name'] or 'Trailer' in x['name'] and x['site'] == 'YouTube'):
                        movieDetails['trailer'] = youtube_embed_link + x['key']
                    elif(x['type'] == 'Trailer' and x['site'] == 'YouTube' and len(response.json()['results']) == 1 ):
                        movieDetails['trailer'] = youtube_embed_link + x['key']



                return movieDetails

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()

    window.show()
    sys.exit(app.exec_())
