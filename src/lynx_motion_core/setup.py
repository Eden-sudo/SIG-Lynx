import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'lynx_motion_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'lynx_motion_core'), glob(os.path.join('lynx_motion_core', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Eden',
    maintainer_email='caedulu2305@gmail.com',
    description='Núcleo de cálculo, visión y control cinemático para AL5D Lynxmotion',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'vision_service = lynx_motion_core.vision_service:main',
            'calculus_service = lynx_motion_core.calculus_service:main',
            'motion_service = lynx_motion_core.motion_service:main',
        ],
    },
)
