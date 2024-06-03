from cx_Freeze import setup, Executable
import os

# Define the files and directories to be included in the build
includefolders = [
    'frontend/',       # Include the entire frontend directory
    'songsData/',      # Include the entire songsData directory
    'songsWav/',       # Include the entire songsWav directory
    'frontend/images/',
    # Add other necessary files or directories
]
# includes = [
#     # #'tslearn.metrics.pairwise',
#     # #'tslearn.backend.numba_backend',
#     # #'tslearn.backend.dtypes',
#     # 'tslearn.backend',
#     # 'sklearn.utils',
#     # 'sklearn.metrics',
#     # 'sklearn.metrics.pairwise',
#     # # 'tslearn.backend.instantiate_backend',
#     # # 'tslearn.backend.numpy_backend.NumPyBackend',
#     # # 'sklearn.metrics.pairwise.euclidean_distances',
#     # # 'sklearn.metrics.pairwise.pairwise_distances'
# ]

includes = [
    'frontend.main',
    'frontend.MainContent',
    'frontend.OutOfTune',
    'frontend.Sidebar',
    'frontend.SongComponent',
    'frontend.SpotifyUI',
    'frontend.VirtualPiano'
]


excludes = [
    # 'sklearn.tests',
    # 'sklearn.externals',
    # 'tensorflow.examples',
]
packages = [
    'crepe',
    'pyaudio',
    'pymongo',
    'matplotlib',
    'tensorflow',
    'tensorflow.python',
    'numpy',
    'sklearn',
    'tslearn',
    # 'tslearn.metrics',
    # 'tslearn.backend',
    # 'sklearn.utils',
    # 'sklearn.metrics',
    # 'sklearn.metrics.pairwise',
    'scipy',  # often required by sklearn
    'joblib',  # used by sklearn for model persistence
    'threadpoolctl',  # another sklearn dependency
]

# Add all individual .py files in the frontend directory
frontend_files = [
    'frontend/main.py',
    'frontend/MainContent.py',
    'frontend/OutOfTune.py',
    'frontend/Sidebar.py',
    'frontend/SongComponent.py',
    'frontend/SpotifyUI.py',
    'frontend/VirtualPiano.py'
]

backend_files = [
    'compare.py',
    'db_persistence_layer.py',
    'filesAccess.py',
    'mainTesting.py',
]

# Base can be "Win32GUI" or "Console" for Windows
base = None  #base='Console' for console and GUI

if os.name == 'nt':
    base = 'Win32GUI'  # Use 'Console' if you have a console application
    #base = 'Console'

executables = [
    #Executable('frontend/main.py', base=base, target_name='OutOfTuneV1')    #causes file main.py (for module main) not found, line below fixes it
    Executable('mainTesting.py', base=base, target_name='OutOfTuneV1')

]

output_dir = r'C:\atestingApp\cxFreeze\V9'  # New output directory
os.makedirs(output_dir, exist_ok=True)




build_exe_options = {
    'packages': packages,
    'excludes': excludes,
    'includes': includes,
    'include_files': includefolders + frontend_files + backend_files,  # Include all specified files and directories
    'build_exe': output_dir,
    #'zip_include_packages': ['tensorflow', 'sklearn', 'scipy', 'tslearn']
}

setup(
    name='OutOfTuneV1',
    version='1.0',
    description='Out Of Tune',
    options={'build_exe': build_exe_options},
    executables=executables,
)
