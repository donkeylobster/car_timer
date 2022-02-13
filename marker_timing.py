# -*- coding: utf-8 -*-
"""
Created on Fri Feb 11 21:21:42 2022

@author: thlu
"""
from dataclasses import dataclass, field
from typing import List
import time, datetime

@dataclass
class Marker_data:
    id: int
    in_box: bool
    last_change: float = 0
    last_seen: float = field(default_factory=time.time)
    racing: int = -1
    time_start: float = 0
    time_end: float = 0

    # def __repr__(self):
    #     return str(self.id)

    def __eq__(self, other) -> bool:
        return self.id == other

@dataclass
class Active_markers:
    markers: List[Marker_data]

    def __iter__(self):
        yield from (self.markers)

    def update(self, id, in_box):
        index = self.find(id)
        if index >= 0:
            # print(id, "in", index)

            if self.markers[index].racing == -1:
                # outside box, not in box yet
                if in_box:
                    # now in box, ready to start
                    self.markers[index].racing  = 0
                    self.markers[index].in_box = True
                    self.markers[index].last_change = time.time()
                else:
                    # Still outside box, no change
                    pass
            elif self.markers[index].racing == 0:
                # In box, ready to start
                if in_box:
                    # Still in box, bo change
                    pass
                else:
                    # Now out of box, start racing
                    self.markers[index].racing  = 1
                    self.markers[index].in_box = False
                    self.markers[index].last_change = time.time()
                    self.markers[index].time_start = time.time()
            elif self.markers[index].racing == 1:
                # Racing, time is running...
                if in_box:
                    # Done racing, stop timer
                    self.markers[index].racing  = 2
                    self.markers[index].in_box = True
                    self.markers[index].last_change = time.time()
                    self.markers[index].time_end = time.time()
                else:
                    # Still racing
                    pass
            elif self.markers[index].racing == 2:
                # Race done.
                # TODO: How to reset?
                pass
            else:
                print("Error var racing wrong value")

            # update hardbead
            self.markers[index].last_seen = time.time()


        else:
            self.markers.append(Marker_data(id, in_box))
            # print(id, "Added!")

    def find(self, id):
        if id not in self.markers:
            return -1
        for i,marker in enumerate(self.markers):
            if marker == id:
                break
        return i


    def status_text(self):
        t = ""
        for marker in self.markers:
            t += "Bil {:02d}".format(marker.id)
            if marker.racing == 1:
                seconds = round(time.time()-marker.time_start,2)
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                t += " Racing\t{:.0f}:{:02.0f}:{:02.02f}".format(h, m, s)
            elif marker.racing == 2:
                seconds = round(marker.time_end-marker.time_start,2)
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                t += " Done\t{:.0f}:{:02.0f}:{:02.02f}".format(h, m, s)
            elif marker.racing == 0 and marker.in_box:
                t += " Ready to start! "
            t += "\n"
        return t



if __name__ == '__main__':

    markers_seen = Active_markers([])
    
    markers_seen.update(1, False)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    markers_seen.update(1, True)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    markers_seen.update(1, False)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    time.sleep(.4)
    
    markers_seen.update(1, False)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    time.sleep(.3)
    
    markers_seen.update(1, True)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    markers_seen.update(1, False)
    print(markers_seen.status_text())
    # print(markers_seen)
    
    
    
    
    
    
