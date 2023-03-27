from setuptools import setup, find_packages
setup(
    name = 'library_manager',
    version= '0.1.0',
    description='database application to manage books for a library',
    author='Canrong Qiu (Jackey)',
    author_email='canrong.qiu@desy.de',
    url='https://github.com/jackey-qiu/Library_Manager',
    classifiers=['Topic :: mongodb application',
                 'Programming Language :: Python'],
    license='MIT',
    install_requires=['PyQt5','pyqtgraph','pymongo','python-dotenv','pandas','bcrypt','dnspython'],
    packages=find_packages(),
    # packages=find_packages(where='library_manager'),
    # package_dir={'': 'library_lanager'},
    package_data={'':['*.ui','*.svg','*.qss','*.xml','*.pngn','*.dot'],'.library_manger.resources':['icons/*.*','./library_manager/resources/private/*.*']},
    scripts=['./library_manager/bin/manager_gui.py'],
    entry_points = {
        'console_scripts' : [
            'lib = library_manager.bin.manager_gui:main'
        ],
    }
)