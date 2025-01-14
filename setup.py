from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = ''.join(f.readlines())

print(find_packages())

setup(
    name='speech-recognition',
    version='0.1',
    keywords='Speech Recognition',
    description='End2End Speech Recognition using Deep Learning',
    long_description=long_description,
    author='wan87',
    author_email='wan877@gmail.com',
    license='MIT',
    url='https://github.com/wan87',
    zip_safe=False,
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'speechrecognition = speechrecognition.main:speech',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)