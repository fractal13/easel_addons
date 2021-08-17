#!/usr/bin/env python3

import re
import sys
import datetime
import os
import easel.helpers_yaml
import easel.component

def display_iso_8601(dt, ds_start_month, ds_start_day, ds_end_month, ds_end_day, ds_offset):
    s = dt.isoformat()
    if (dt.month > ds_start_month) or (dt.month == ds_start_month and dt.day >= ds_start_day):
        started = True
    else:
        started = False

    if (dt.month < ds_end_month) or (dt.month == ds_end_month and dt.day < ds_end_day):
        ended = False
    else:
        ended = True

    if started and not ended:
        ds_offset -= 1

    s = "{}-{:02d}:00".format(s, ds_offset)
    return s

def get_assignment_dates(my_args):
    full_path = os.path.join(my_args['web_dir'], my_args['schedule_filename'])
    if not os.path.exists(full_path):
        raise Exception(full_path + " does not exist.")

    asst_column = my_args['asst_column']
    date_column = my_args['date_column']
    year = my_args['year']
    hour = my_args['hour']
    minute = my_args['minute']

    daylight_savings_start_month = my_args['daylight_savings_start_month']
    daylight_savings_start_day = my_args['daylight_savings_start_day']
    daylight_savings_end_month = my_args['daylight_savings_end_month']
    daylight_savings_end_day = my_args['daylight_savings_end_day']
    daylight_savings_offset = my_args['daylight_savings_offset']

    assignment_dates = {}

    fin = open(full_path, "r")
    for line in fin:
        line = line.strip()
        words = line.split('|')
        if len(words) > asst_column and len(words) > date_column:
            date = words[date_column].strip()
            asst = words[asst_column].strip()
            try:
                date2 = datetime.datetime.strptime(date, "%b %d")
                date2 = date2.replace(year=year, hour=hour, minute=minute)
                fancy_date = display_iso_8601(date2, daylight_savings_start_month, daylight_savings_start_day,
                                              daylight_savings_end_month, daylight_savings_end_day,
                                              daylight_savings_offset)
                
                assignments = asst.split(",")
                for asst in assignments:
                    assignment_dates[asst] = fancy_date
            except ValueError as e:
                pass
            
    fin.close()

    return assignment_dates

def main(argv):
    my_args = {
        'web_dir': "dsu-cs-3530-theory-web/web",        
        'schedule_filename': "schedule.md",
        'canvas_dir': "dsu-cs-3530-canvas",
        'date_column': 0,
        'asst_column': 3,
        'year': 2021,
        'hour': 8,
        'minute': 55,
        'daylight_savings_start_month': 3,
        'daylight_savings_start_day': 14,
        'daylight_savings_end_month': 11,
        'daylight_savings_end_day': 7,
        'daylight_savings_offset': 7,
    }

    assignment_dates = get_assignment_dates(my_args)
    
    #print(assignment_dates)
    for asst in assignment_dates:
        # remove *
        asst_name = asst.replace('*', '')
        canvas_assignment = easel.component.gen_filename(my_args['canvas_dir']+'/assignments', asst_name)
        ## canvas_assignment = "{}/assignments/{}.yaml".format(my_args['canvas_dir'], asst)
        if os.path.exists(canvas_assignment):
            easel_assignment = easel.helpers_yaml.read(canvas_assignment)
            easel_assignment.due_at = assignment_dates[asst]
            easel.helpers_yaml.write(canvas_assignment, easel_assignment)
        else:
            print("{}({}) does not exist.".format(asst, canvas_assignment))

    return

if __name__ == "__main__":
    main(sys.argv)
