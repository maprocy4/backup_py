#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import shutil

def make_diffs(storage, backup):
    # 1) Create lists of files in _storage_ and _backup_;
    # 2) By this 2 lists create 2 another lists:
    #       diffs_backup - list of files, which are exist in _backup_, 
    #       but not exist in _storage_,
    #       and
    #       diffs_storage - list of files, which are exist in _storage_,
    #       but not exist in _backup_.
    
    storage_flist = []
    backup_flist = []
    diffs_storage = []
    diffs_backup = []
    collisions_list = []
    diffs_dict = {}
    
    # List storage_flist: all files in _storage_ directory with their pathes and sizes
    for root, dirs, files in os.walk(storage):
        spec_root = root
        abstr_root = root.replace(storage, "")
        for filename in files:
            spec_filepath = os.path.join(spec_root, filename)
            abstr_filepath = os.path.join(abstr_root, filename)
            filesize = os.path.getsize(spec_filepath)
            file_entry = [abstr_filepath, filesize]
            storage_flist.append(file_entry)
          
    # List backup_flist: all files in _backup_ directory with their pathes and sizes
    for root, dirs, files in os.walk(backup):
        spec_root = root
        abstr_root = root.replace(backup, "")
        for filename in files:
            spec_filepath = os.path.join(spec_root, filename)
            abstr_filepath = os.path.join(abstr_root, filename)
            filesize = os.path.getsize(spec_filepath)
            file_entry = [abstr_filepath, filesize]
            backup_flist.append(file_entry)

    # List diffs_storage[] - files, which are exist in _storage_, but not exist in _backup_
    for file_entry in storage_flist:
        if file_entry not in backup_flist:
            diffs_storage.append(file_entry)

    # List diffs_backup[] - files, which are exist in _backup_, but not exist in _storage_
    for file_entry in backup_flist:
        if file_entry not in storage_flist:
            diffs_backup.append(file_entry)

    # List collisions_list[] - files with same names, but different sizes, in _storage_ and _backup_
    for file_entry_strg in storage_flist:
        for file_entry_bup in backup_flist:
            if file_entry_strg[0] == file_entry_bup[0] and file_entry_strg[1] != file_entry_bup[1]:
                collisions_list.append(file_entry_strg[0])

    diffs_dict['diffs_storage'] = diffs_storage
    diffs_dict['diffs_backup'] = diffs_backup
    diffs_dict['collisions_list'] = collisions_list

    return diffs_dict

def backup_no_delete(storage, backup, verbose):
    # If key --delete/-d is not set, then files which are exist in _backup_, 
    # but not exist in _storage_ will be copied to _storage_; files which are
    # exist in _storage_, but not exist in _backup_, will be copied
    # to _backup_.
    # If file wtih same name exists both in _storage_ and _backup_, but have 
    # different sizes, file in _backup_ will be renamed to %filename%__old 
    # and copied to _storage_; file from _storage_ will be copied to _backup_.


    # Algorithm:
    # 1) Create lists of files ~backup~ and ~storage~;
    # 2) Based on these lists, create 2 lists: 
    #       diffs_backup - list of files, which are exist in _backup_, 
    #       but not exist in _storage_,
    #       and
    #       diffs_storage - list of files, which are exist in _storage_,
    #       but not exist in _backup_,
    #       collisions_list - list of files, which are exist both in _storage_
    #       and backup, but have different sizes.
    # 3) Operate!

    diffs = make_diffs(storage, backup)

    # 1) Files, which are exist both in _storage_ and backup, but have different sizes:
    #       file in _backup_ will be renamed to %filename%__old and copied to _storage_; 
    #       file from _storage_ will be copied to _backup_.
    print("%i file(s) with same name(s) both in %s and %s have different sizes. Archiving..." % (len(diffs['collisions_list']), storage, backup))

    for file_entry in diffs['collisions_list']:
        path, filename = os.path.split(file_entry)
        arch_filename = filename + '__old'
        strg_path = os.path.join(storage, path)
        bup_path = os.path.join(backup, path)
        shutil.move(os.path.join(bup_path, filename), os.path.join(bup_path, arch_filename))
        shutil.copy(os.path.join(bup_path, arch_filename), os.path.join(strg_path, arch_filename))
        shutil.copy(os.path.join(strg_path, filename), os.path.join(bup_path, filename))
        if verbose == True:
            print("Archived: %s..." % (file_entry,))

    # 2) Files, which are exist in _backup_, but not exist in _storage_, will be copied
    #       to _storage_.
    # copy diffs_dict['diffs_backup'] -> storage
    print("Updating storage: %s - from backup: %s - with %i files..." % (storage, backup, len(diffs['diffs_backup'])))
    
    for file_entry in diffs['diffs_backup']:
        if file_entry[0] not in diffs['collisions_list']:
            path, filename = os.path.split(file_entry[0])
            dst_path = os.path.join(storage, path)
            src_path = os.path.join(backup, path)
            try:
                os.makedirs(dst_path, mode=0o755)
            except OSError:
                shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
                if verbose == True:
                    print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))
            else:
                shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
                if verbose == True:
                    print("Directory created: %s" % dst_path)
                    print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))
        
    # 3) Files, which are exist in _storage_, but not exist in _backup_, will be copied
    #   to _backup_.
    # copy diffs_dict['diffs_storage'] -> backup
    print("Updating backup: %s - from storage: %s - with %i files..." % (backup, storage, len(diffs['diffs_storage'])))
    
    for file_entry in diffs['diffs_storage']:
        if file_entry[0] not in diffs['collisions_list']:
            path, filename = os.path.split(file_entry[0])
            dst_path = os.path.join(backup, path)
            src_path = os.path.join(storage, path)
            try:
                os.makedirs(dst_path, mode=0o755)
            except OSError:
                shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
                if verbose == True:
                    # print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))
                    pass 
            else:
                shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
                if verbose == True:
                    print("Directory created: %s" % dst_path)
                    print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))

def backup_with_delete(storage, backup, verbose):
    # If key --delete/-d is set, then files, which are exist in _backup_,
    # but not exist in _storage_, will be deleted; files, which are exist
    # in _storage_, but not exist in _backup_, will be copied to _backup_.
    # If file exists both in _storage_ and _backup_, but have different sizes,
    # file in _backup_ will be deleted.
    
    diffs = make_diffs(storage, backup)

    # 1) Files, which are exist in _backup_, but not exist in _storage_,
    #       will be deleted. Empty directories will be deleted too.
    print("Clearing backup: %s  - %i files will be deleted..." % (backup, len(diffs['diffs_backup'])))
    
    for file_entry in diffs['diffs_backup']:
        real_filepath = os.path.join(backup, file_entry[0])
        os.remove(real_filepath)
        print("File deleted: %s" % real_filepath)

    # Delete all empty directories in _backup_
    for root, dirs, files in os.walk(backup, topdown=False):
        for directory in dirs:
            try:
                os.rmdir(os.path.realpath(os.path.join(root, directory)))
            except OSError:
                pass

    # 2) Files, which are exist in _storage_, but not exist in _backup_, will be copied
    #   to backup.
    # copy diffs_dict['diffs_storage'] -> backup
    print("Updating backup: %s - from storage: %s  - with %i files..." % (backup, storage, len(diffs['diffs_storage'])))
                
    for file_entry in diffs['diffs_storage']:
        path, filename = os.path.split(file_entry[0])
        dst_path = os.path.join(backup, path)
        src_path = os.path.join(storage, path)
        try:
            os.makedirs(dst_path, mode=0o755)
        except OSError:
            shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
            if verbose == True:
                print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))
        else:
            shutil.copy(os.path.join(src_path, filename), os.path.join(dst_path, filename))
            if verbose == True:
                print("Directory created: %s" % dst_path)
                print("File copied: %s -> %s" % (os.path.join(src_path, filename), os.path.join(dst_path, filename)))

def main():
    parser = argparse.ArgumentParser(
        description="""Brings _backup_ in line with _storage_.
If key --delete/-d is not set, then files, which are exist in _backup_, but
not exist in _storage_, will be copied to storage; files, which are exists in
_storage_, but not exist in _backup_, will be copied to _backup_;
if file with same name exists both in _storage_ and _backup_, but have 
different sizes, file in _backup_ will be renamed to %filename%__old 
and copied to _storage_, file from _storage_ will be copied to _backup_.\n
If key --delete/-d is set, then files, which are exists in backup,
but not exist in _storage_, will be deleted; files which are exist in _storage_,
but not exist in _backup_, will be copied to _backup_; if file with same name 
exists both in _storage_ and _backup_, but have different sizes, file in 
_backup_ will be deleted, file from _storage_ will be copied to _backup_. """,
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("storage", metavar="_storage_", type=str, nargs=1,
                        help="directory with data to backup.")
    parser.add_argument("backup", metavar="_backup_", type=str, nargs=1,
                        help="directory where to backup.")
    parser.add_argument("--delete", action="store_true", help="Delete from _backup_ files, which are not exist in storage.")
    parser.add_argument("-d", action="store_true", help="Delete from _backup_ files, which are not exist in storage.")
    parser.add_argument("--verbose", action="store_true", help="Enable \"verbose\" mode.")
    parser.add_argument("-v", action="store_true", help="Enable \"verbose\" mode.")
    
    args = parser.parse_args()
    
    # print(args)                 # Debug output
    # print(args.storage[0])

    if args.v == True or args.verbose == True:
        verbose = True
    else:
        verbose = False

    if args.d == True or args.delete == True:
        backup_with_delete(args.storage[0], args.backup[0], verbose)
    else:
        backup_no_delete(args.storage[0], args.backup[0], verbose)

if __name__ == "__main__":
    main()
