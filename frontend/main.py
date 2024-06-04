# main.py
from frontend.OutOfTune import OutOfTune
from frontend.SpotifyUI import SpotifyUI

if __name__ == "__main__":

    #oot = OutOfTune("Roni")
    #oot.getSongData("Menagev lah et Hadmaot.wav", True, oot)
    app = SpotifyUI()
    app.mainloop()
