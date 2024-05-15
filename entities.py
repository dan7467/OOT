# for simplicity, we didn't wrap every object in our project with DTW, since most of them don't change.
# instead, we only wrap user-specific-data, such as user performances and grades

class user_application_state_DTW:
    def __init__(self, userId):
        self.userId = userId
        self.user_performances = []

    def addUserPerformance(self, userPerformance):
        self.user_performances.append(userPerformance)


#

class userPerformanceDTW:
    def __init__(self, userId, performanceId, grade, songName, dictOfPerformanceNotesDict):
        self.userId = userId
        self.performanceId = performanceId
        self.grade = grade
        self.songName = songName
        self.performanceNotesDict = [] # a 'one-to-many' relation, instances of performanceNotesDict

    def add_performance(self, performanceNotesDict):
        self.performanceNotesDict.append(performanceNotesDict)


#

class performanceNotesDictDTW:
    def __init__(self, performanceId, songName, frequency, time):
        self.performanceId = performanceId
        self.songName = songName
        self.frequency = frequency
        self.time = time
