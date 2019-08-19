from django.shortcuts import render,redirect,reverse,HttpResponseRedirect

import mysql.connector
from django.http import HttpResponse,JsonResponse
import json
from datetime import datetime



# Create your views here.

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="mohamed98"
)


mycursor = mydb.cursor(buffered=True,dictionary=True)


def show_db():
  mycursor.execute("SHOW DATABASES")
  for x in mycursor:
    print(x)


def conect_db(dbname):
  mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="mohamed98",
    database="{}".format(dbname)
  )


def show_tab():
  mycursor.execute("SHOW TABLES")
  for x in mycursor:
    print(x)


def excute_sql(sql):
    mycursor.execute(sql)
    result = mycursor.fetchall()
    return result


mycursor.execute('USE familyTree')


def get_family_members_id():
    sql = F" SELECT familyMember_id FROM familyMembers"
    result = excute_sql(sql)
    family_members_id_list = []
    for record in result:
        family_members_id_list.append(int(record["familyMember_id"]))
    return family_members_id_list


def get_non_family_members_id():
    sql = F" SELECT person_id FROM non_family_members"
    result = excute_sql(sql)
    non_family_members_id_list = []
    for record in result:
        non_family_members_id_list .append(int(record["person_id"]))
    return non_family_members_id_list


def get_all_persons():
    sql = F" SELECT national_id FROM Person"
    result = excute_sql(sql)
    person_id_list = []
    for record in result:
        person_id_list.append(int(record['national_id']))
    return person_id_list


# >>>>>>>>>>>>>>>> get ROOT brothers/sisters <<<<<<<<<<<<<<<<
def root_children():
    root_query = F"""
            select familyMember_id
                    from familyMembers
                        where  father_id is NULL """
    root_result = excute_sql(root_query)

    fatherid_list = []
    for fatherid in root_result :
        fatherid_list.append(fatherid[0])

    root_child = []
    for dadId in fatherid_list:
        child_query = F"""
                    select familyMember_id
                            from familyMembers
                                where  father_id = {dadId}"""
        result = excute_sql(child_query)
        root_child.append(result)

    last_root_child = []
    for childsID_list in root_child:
        for childsID in childsID_list:
            last_root_child.append(childsID[0])
    return last_root_child

def get_root():
    last_root_child = root_children()
    root = []
    for child in last_root_child:
        dad_query = F"""select father_id from familyMembers where familyMember_id = {child};"""
        mom_query = F"""select mother_id from familyMembers where familyMember_id = {child};"""
        dad_result = excute_sql(dad_query)
        mom_result = excute_sql(mom_query)

        fatherID = dad_result[0][0]
        motherID = mom_result[0][0]
        if fatherID in get_family_members_id():
            root.append(fatherID)
        elif motherID in get_family_members_id():
            root.append(motherID)
    return list(set(root))


# >>>>>>>>>>>>>>>> get parents' parent <<<<<<<<<<<<<<<<
grandma = []
grandpa = []

def get_grand_ma(person_id):
    if int(person_id) in get_family_members_id():
        mom_result = excute_sql(F"SELECT mother_id FROM familyMembers WHERE familyMember_id = {person_id}")
        mother_id = [id["mother_id"] for id in mom_result][0]
        if not mother_id:
            return grandma
        else:
            grandma.append(mother_id)
            return get_grand_ma(mother_id)

    elif int(person_id) in get_non_family_members_id():
        mom_result = excute_sql(F"SELECT mother_id FROM non_family_members WHERE person_id = {person_id}")
        mother_id = [id["mother_id"] for id in mom_result][0]
        if not mother_id:
            return grandma
        else:
            grandma.append(mother_id)
            return get_grand_ma(mother_id)
    else:
        return grandma


def get_grand_pa(person_id):
    if not person_id:
        return []
    else:
        if int(person_id) in get_family_members_id():
            dad_result = excute_sql(F"SELECT father_id FROM familyMembers WHERE familyMember_id = {person_id}")
            father_id = dad_result[0]["father_id"]

            if not father_id:
                return grandpa
            else:
                grandpa.append(father_id)
                return get_grand_pa(father_id)

        elif int(person_id) in get_non_family_members_id():
            dad_result = excute_sql(F"SELECT father_id FROM non_family_members WHERE person_id = {person_id}")
            father_id = dad_result[0]["father_id"]


            if not father_id:
                return grandpa
            else:
                grandpa.append(father_id)
                return get_grand_pa(father_id)
        else:
            return grandpa


def grand_parents(person_id):
    if int(person_id) in get_all_persons():
        result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
        person_gender = result[0]['gender'].decode()

        if person_gender == "male":
            try:
                try:
                    his_dad_query = excute_sql(
                        F"SELECT father_id FROM familyMembers WHERE familyMember_id = {int(person_id)}")
                    his_dad = his_dad_query[0]["father_id"]
                    grand_mothers = get_grand_ma(his_dad)
                except IndexError:
                    his_dad_query = excute_sql(
                        F"SELECT father_id FROM non_family_members WHERE person_id = {person_id}")
                    his_dad = his_dad_query[0]["father_id"]
                    grand_mothers = get_grand_ma(his_dad)

                grand_mothers += get_grand_ma(person_id)
                return grand_mothers

            except:
                return []

        elif person_gender == "female":
            try:
                try:
                    her_dad_query = excute_sql(
                        F"SELECT father_id FROM familyMembers WHERE familyMember_id = {person_id}")
                    her_dad = her_dad_query[0]["father_id"]
                    grand_father = get_grand_pa(her_dad)
                except IndexError:
                    her_dad_query = excute_sql(
                        F"SELECT father_id FROM non_family_members WHERE person_id = {person_id}")
                    her_dad = her_dad_query[0]["father_id"]
                    grand_father = get_grand_pa(her_dad)

                grand_father += get_grand_pa(person_id)
                return grand_father
            except:
                return []
    else:
        return []


# >>>>>>>>>>>>>>>> get parents <<<<<<<<<<<<<<<<
def get_mother(family_member_id):
    if int(family_member_id) in get_family_members_id():
        query = F"""
                    select mother_id
                    from familyMembers
                    where familyMember_id = {family_member_id};
            """
        result = excute_sql(query)
        motherID = result[0]["mother_id"]
        motherID_list = []
        if not motherID:
            return []
        else:
            motherID_list.append(motherID)
            return motherID_list
    else:
        query = F"""
                                    select mother_id
                                    from non_family_members
                                        where person_id = {family_member_id};"""
        result = excute_sql(query)

        motherID = result[0]["mother_id"]

        motherID_list= []
        if not motherID:
            return motherID_list
        else:
            motherID_list.append(motherID)
            return motherID_list


def get_father(family_member_id):
    if int(family_member_id) in get_family_members_id():
        query = F"""
                    select father_id
                    from familyMembers
                        where familyMember_id = {family_member_id};"""
        result = excute_sql(query)

        fatherID = result[0]["father_id"]
        fatherID_list = []
        if not fatherID:
            return []
        else:
            fatherID_list.append(fatherID)
            return fatherID_list
    else:
        query = F"""
                            select father_id
                            from non_family_members
                                where person_id = {family_member_id};"""
        result = excute_sql(query)
        fatherID = result[0]["father_id"]
        fatherID_list = []
        if not fatherID:
            return []
        else:
            fatherID_list.append(fatherID)
            return fatherID_list


def get_parents(person_id):
    if int(person_id) in get_all_persons():
        result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
        person_gender = result[0]["gender"].decode()
        if person_gender == "male":
            mother = get_mother(person_id)
            return mother
        elif person_gender == "female":
            father = get_father(person_id)
            return father
    else:
        return []


# >>>>>>>>>>>>>>>> get Female/Male childrens <<<<<<<<<<<<<<<<
def get_female_childrens(parent_id):
    parent_gender = excute_sql(F"SELECT gender FROM Person WHERE national_id = {parent_id}")[0]["gender"].decode()

    female_children_list = []
    if int(parent_id) in get_family_members_id():
        if parent_gender == "female":
            her_husbands = get_parteners(parent_id)

            for hus in her_husbands:
                if hus in get_family_members_id():
                    sql_female_children = F'''
                                SELECT fm.familyMember_id
                                        FROM familyMembers fm 
                                        INNER JOIN Person p
                                        ON fm.familyMember_id = p.national_id
                                            WHERE p.gender = 'female' AND fm.mother_id = {parent_id}
                    '''
                    female_children_ = [id["familyMember_id"] for id in excute_sql(sql_female_children)]

                    for record in female_children_:
                        female_children_list.append(record)

                elif hus not in get_family_members_id():
                    sql_female_children = F'''
                                                    SELECT nfm.person_id
                                                            FROM non_family_members nfm
                                                            INNER JOIN Person p
                                                            ON nfm.person_id = p.national_id
                                                                WHERE p.gender = 'female' AND nfm.mother_id = {parent_id}
                                        '''
                    female_children_ = [id["person_id"] for id in excute_sql(sql_female_children)]
                    for record in female_children_:
                        female_children_list.append(record)

        elif parent_gender == "male":
            sql_female_children= F'''
                                SELECT fm.familyMember_id
                                        FROM familyMembers fm 
                                        INNER JOIN Person p
                                        ON fm.familyMember_id = p.national_id
                                            WHERE p.gender = 'female' AND fm.father_id= {parent_id}
                    '''

            female_children_ = [id["familyMember_id"] for id in  excute_sql(sql_female_children)]

            for record in female_children_:
                female_children_list.append(record)

    elif parent_id not in get_family_members_id():
        if parent_gender == "female":
            her_husbands = get_parteners(parent_id)

            if not her_husbands:
                sql_female_children = F'''
                            SELECT nfm.person_id
                            FROM non_family_members nfm
                            INNER JOIN Person p
                            ON nfm.person_id = p.national_id
                            WHERE p.gender = 'female' AND nfm.mother_id = {parent_id}
                                                    '''
                female_children = [id["person_id"] for id in excute_sql(sql_female_children)]

                for record in female_children:
                    female_children_list.append(record)

            else:
                for hus in her_husbands:
                    if hus in get_family_members_id():
                        sql_female_children = F'''
                                    SELECT fm.familyMember_id
                                            FROM familyMembers fm 
                                            INNER JOIN Person p
                                            ON fm.familyMember_id = p.national_id
                                                WHERE p.gender = 'female' AND fm.father_id = {hus}
                        '''
                        female_children_ = [id["familyMember_id"] for id in excute_sql(sql_female_children)]

                        for record in female_children_:
                            female_children_list.append(record)

        elif parent_gender == "male":
            sql_female_children = F'''
                                        SELECT nfm.person_id
                                        FROM non_family_members nfm
                                        INNER JOIN Person p
                                        ON nfm.person_id = p.national_id
                                        WHERE p.gender = 'female' AND nfm.father_id = {parent_id}
                                                                '''

            female_children_ = [id["person_id"] for id in excute_sql(sql_female_children)]

            for record in female_children_:
                female_children_list.append(record)

    return female_children_list


def get_male_childrens(parent_id):
    parent_gender = excute_sql(F"SELECT gender FROM Person WHERE national_id = {parent_id}")[0]["gender"].decode()

    male_children_list = []

    if int(parent_id) in get_family_members_id():
        if parent_gender == "female":
            her_husbands = get_parteners(parent_id)

            if not her_husbands:
                sql_male_children = F'''
                            SELECT fm.familyMember_id
                            FROM familyMembers fm 
                            INNER JOIN Person p
                            ON fm.familyMember_id = p.national_id
                            WHERE p.gender = 'male' AND fm.mother_id= {parent_id}
                                                    '''
                male_children = [ id["familyMember_id"] for id in excute_sql(sql_male_children)]

                for record in male_children:
                    male_children_list.append(record)

            else:
                for hus in her_husbands:
                    if hus in get_family_members_id():
                        sql_male_children = F'''
                                        SELECT fm.familyMember_id
                                                FROM familyMembers fm 
                                                INNER JOIN Person p
                                                ON fm.familyMember_id = p.national_id
                                                    WHERE p.gender = 'male' AND fm.mother_id = {parent_id}
                            '''

                        male_children_ = [id["familyMember_id"] for id in excute_sql(sql_male_children)]

                        for record in male_children_:
                            male_children_list.append(record)

                    elif hus not in get_family_members_id():
                        sql_male_children = F'''
                                    SELECT nfm.person_id
                                    FROM non_family_members nfm
                                    INNER JOIN Person p
                                        ON nfm.person_id = p.national_id
                                            WHERE p.gender = 'male' AND nfm.mother_id = {parent_id}
                                                                '''
                        male_children_ = [id["person_id"] for id in excute_sql(sql_male_children)]

                        for record in male_children_:
                            male_children_list.append(record)

        elif parent_gender == "male":
            sql_male_children = F'''
                                    SELECT fm.familyMember_id
                                            FROM familyMembers fm 
                                            INNER JOIN Person p
                                            ON fm.familyMember_id = p.national_id
                                                WHERE p.gender = 'male' AND fm.father_id= {parent_id}
                        '''
            male_children_ = [id["familyMember_id"] for id in excute_sql(sql_male_children)]

            for record in male_children_:
                male_children_list.append(record)

    elif int(parent_id) not in get_family_members_id():
        if parent_gender == "female":
            her_husbands = get_parteners(parent_id)

            if not her_husbands:
                sql_male_children = F'''
                            SELECT nfm.person_id
                            FROM non_family_members nfm
                            INNER JOIN Person p
                            ON nfm.person_id = p.national_id
                            WHERE p.gender = 'male' AND nfm.mother_id = {parent_id}
                                                    '''
                male_children = [ id["person_id"] for id in excute_sql(sql_male_children)]

                for record in male_children:
                    male_children_list.append(record)
            else:
                for hus in her_husbands:
                    if hus in get_family_members_id():
                        sql_male_children = F'''
                                                SELECT fm.familyMember_id
                                                        FROM familyMembers fm 
                                                        INNER JOIN Person p
                                                        ON fm.familyMember_id = p.national_id
                                                            WHERE p.gender = 'male' AND fm.father_id = {hus}
                                    '''
                        male_children = [id["familyMember_id"] for id in excute_sql(sql_male_children)]

                        for record in male_children:
                            male_children_list.append(record)

    return male_children_list


def get_childrens(person_id,all=False):
    if not all:
        if int(person_id) in get_all_persons():
            person_gender = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")[0]["gender"].decode()
            if person_gender == "male":
                female_childrens = get_female_childrens(person_id)
                return female_childrens
            elif person_gender == "female":
                male_children = get_male_childrens(person_id)
                return male_children
        else:
             return []
    if all:
        if int(person_id) in get_all_persons():
                childrens = get_female_childrens(person_id) + get_male_childrens(person_id)
                return childrens
        else:
             return []


# >>>>>>>>>>>>>>>> get Sisters/Brothers <<<<<<<<<<<<<<<<
def get_sisters(person_id,alive=False):
    try:
        father_id = excute_sql(F"SELECT father_id from familyMembers where familyMember_id = {person_id}")[0]["father_id"]
        if not father_id:
            return []
        if alive:
            sql_sister_query = F"""
                            Select familyMember_id
                            from familyMembers fm
                            INNER JOIN Person p
                            ON fm.familyMember_id = p.national_id
                                where father_id ={father_id} and p.gender = 'female' and p.death_date is NULL;
                       """
        elif not alive:
            sql_sister_query = F"""
                                    Select familyMember_id
                                    from familyMembers fm
                                    INNER JOIN Person p
                                    ON fm.familyMember_id = p.national_id
                                        where father_id ={father_id} and p.gender = 'female';
                        """
        result = [id["familyMember_id"] for id in excute_sql(sql_sister_query)]

    except:
        father_id = excute_sql(F"SELECT father_id FROM non_family_members WHERE person_id = {person_id}")[0]["father_id"]
        if not father_id:
            return []
        else:
            if alive:
                sql_sister_query = F"""
                                    Select person_id
                                    from non_family_members nfm
                                    INNER JOIN Person p
                                    ON nfm.person_id = p.national_id
                                        where father_id ={father_id} and p.gender = 'female' and p.death_date is NULL;
                               """
            elif not alive:
                sql_sister_query = F"""
                                            Select person_id
                                            from non_family_members nfm
                                            INNER JOIN Person p
                                            ON nfm.person_id = p.national_id
                                                where father_id ={father_id} and p.gender = 'female';
                                """

            result = [id["person_id"] for id in excute_sql(sql_sister_query)]

    sisters_list = []
    for record in result:
        sisters_list.append(record)
    return sisters_list


def get_brothers(person_id,alive=False):
    try:
        try:
            father_id = excute_sql(F"SELECT father_id from familyMembers where familyMember_id = {person_id}")[0][
                "father_id"]

            if not father_id:
                return []

            if alive:
                sql_brother_query = F"""
                                Select familyMember_id
                                from familyMembers fm
                                INNER JOIN Person p
                                ON fm.familyMember_id = p.national_id
                                    where father_id ={father_id} and p.gender = 'male' and p.death_date is NULL;
                       """
            elif not alive:
                sql_brother_query = F"""
                                        Select familyMember_id
                                        from familyMembers fm
                                        INNER JOIN Person p
                                        ON fm.familyMember_id = p.national_id
                                            where father_id ={father_id} and p.gender = 'male';
                               """
        except IndexError:
            father_id = excute_sql(F"SELECT father_id FROM non_family_members WHERE person_id = {person_id}")[0][
                "father_id"]
            if not father_id:
                return []
            else:
                if alive:
                    sql_brother_query = F"""
                                                Select person_id
                                                from non_family_members nfm
                                                INNER JOIN Person p
                                                ON nfm.person_id = p.national_id
                                                    where father_id ={father_id} and p.gender = 'male' and p.death_date is NULL;
                                       """
                elif not alive:
                    sql_brother_query = F"""
                                                        Select person_id
                                                        from non_family_members nfm
                                                        INNER JOIN Person p
                                                        ON nfm.person_id = p.national_id
                                                            where father_id ={father_id} and p.gender = 'male';
                                               """

        result = excute_sql(sql_brother_query)
        brothers_list = []
        for record in result:
            brothers_list.append(record["familyMember_id"])

        return brothers_list

    except:
        return []


def brothers_or_sisters(person_id,all=False):
    if not all:
        if int(person_id) in get_all_persons():
            result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
            person_gender = result[0]["gender"].decode()
            if person_gender == "male":
                sisters = get_sisters(person_id)
                return sisters
            elif person_gender == "female":
                brothers = get_brothers(person_id)
                return brothers
            else:
                return []
    elif all:
        if int(person_id) in get_all_persons():
            bro_sis = get_brothers(person_id) + get_sisters(person_id)
            return bro_sis
        else:
            return []

# >>>>>>>>>>>>>>>> get Parteners <<<<<<<<<<<<<<<<
def get_parteners(person_id):
    family_members_id = get_family_members_id()
    person_gender = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")[0]["gender"].decode()

    if int(person_id) in family_members_id:
        query = F'''
                select current_status from familyMembers where familyMember_id = {int(person_id)}
            '''
        my_result = excute_sql(query)[0]["current_status"].decode()
        if my_result == "single":
            return []


        if person_gender == "male":
            wives_id = []
            sql_wives_ids = F"""
                                SELECT partener_id FROM familyMember_marriage
                                        WHERE familyMember_id = {person_id}
            """
            if not sql_wives_ids:
                sql_wives_ids = F"""
                                                SELECT familyMember_id FROM familyMember_marriage
                                                        WHERE partener_id = {person_id}
                            """
                wives_id += [id["familyMember_id"] for id in excute_sql(sql_wives_ids)]
            else:
                wives_id += [id["partener_id"] for id in excute_sql(sql_wives_ids)]

            wives_ids_list = []
            for record in wives_id:
                wives_ids_list.append(record)
            return wives_ids_list


        elif person_gender == "female":
            husbands_id = []
            sql_husband_ids = F"""
                                SELECT partener_id FROM familyMember_marriage
                                        WHERE familyMember_id = {person_id}
            """
            if not sql_husband_ids:
                sql_husband_ids = F"""
                                SELECT familyMember_id FROM familyMember_marriage 
                                WHERE partener_id = {person_id}
                """
                husbands_id += [id["familyMember_id"] for id in excute_sql(sql_husband_ids)]

            else:
                husbands_id += [id["partener_id"] for id in excute_sql(sql_husband_ids)]

            husbands_id_list = []
            for record in husbands_id:
                husbands_id_list.append(record)
            return husbands_id_list


    else:
        if person_gender == "male":
            sql_wives_ids = F"""
                                SELECT familyMember_id FROM familyMember_marriage
                                        WHERE partener_id = {person_id}
            """
            wives_id = [id["familyMember_id"] for id in excute_sql(sql_wives_ids)]

            wives_ids_list = []
            for record in wives_id:
                wives_ids_list.append(record)
            return wives_ids_list

        elif person_gender == "female":
            sql_husband_ids = F"""
                                SELECT familyMember_id FROM familyMember_marriage
                                        WHERE partener_id = {person_id}
            """
            husbands_id = [id["familyMember_id"] for id in excute_sql(sql_husband_ids)]


            husbands_id_list = []
            for record in husbands_id:
                husbands_id_list.append(record)
            return husbands_id_list


# >>>>>>>>>>>>>>>> get Uncles/Aunts <<<<<<<<<<<<<<<<
def get_uncles_or_aunts(person_id):
    person_gender = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")[0]["gender"].decode()

    if person_gender == "male":
        try:
            father_id = excute_sql(F"SELECT father_id FROM familyMembers WHERE familyMember_id = {person_id}")[0]["father_id"]
            try:
                mother_id = excute_sql(F"SELECT mother_id FROM familyMembers WHERE familyMember_id = {person_id}")[0]["mother_id"]
                person_aunts = list(get_sisters(father_id) + get_sisters(mother_id))
                return person_aunts
            except IndexError:
                mother_id = excute_sql(F"SELECT mother_id FROM non_family_members WHERE person_id = {person_id}")[0]["mother_id"]
                person_aunts = list(get_sisters(father_id) + get_sisters(mother_id))
                return person_aunts

        except IndexError:
            return []
    elif person_gender == "female":
        try:
            father_id = excute_sql(F"SELECT father_id FROM familyMembers WHERE familyMember_id = {person_id}")[0]["father_id"]
            try:
                mother_id = excute_sql(F"SELECT mother_id FROM familyMembers WHERE familyMember_id = {person_id}")[0]["mother_id"]
                person_uncles = list(get_brothers(father_id) + get_brothers(mother_id))
                return person_uncles
            except IndexError:
                mother_id = excute_sql(F"SELECT mother_id FROM non_family_members WHERE person_id = {person_id}")[0]["mother_id"]
                person_uncles = list(get_sisters(father_id) + get_sisters(mother_id))
                return person_uncles
        except IndexError:
            return []

# >>>>>>>>>>>>>>>> get Parteners' CHildrens <<<<<<<<<<<<<<<<
def get_childrens_parteners(person_id):
    result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
    person_gender = result[0]["gender"].decode()

    if person_gender == "male":
        children_wives = []
        person_male_children = get_male_childrens(person_id)

        try:
            for id in person_male_children :
                children_wives += [her_id["familyMember_id"] for her_id in get_parteners(id)]
        except:
            for id in person_male_children:
                children_wives += get_parteners(id)

        return children_wives

    elif person_gender == "female":
        children_husbands = []
        person_female_children = get_female_childrens(person_id)

        try:
            for id in person_female_children:
                children_husbands += [his_id["familyMember_id"] for his_id in get_parteners(id)]
        except:
            for id in person_female_children:
                children_husbands += [husband for husband in get_parteners(id)]
        return children_husbands


# >>>>>>>>>>>>>>>> get Parteners' Parents <<<<<<<<<<<<<<<<
def get_partener_parents(person_id):
    result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
    person_gender = result[0]["gender"].decode()

    if person_gender == "male":
        parteners = get_parteners(person_id)
        partener_mothers= []
        for partener in parteners: # recursive is another solution for this

            if get_mother(partener) == None:
                continue
            else:
                partener_mothers += get_mother(partener)
        return partener_mothers

    elif person_gender == "female":
        parteners = get_parteners(person_id)
        partener_fathers = []

        for partener in parteners:
            if get_father(partener) == None:
                continue
            else:
                partener_fathers += get_father(partener)
        return partener_fathers


# >>>>>>>>>>>>>>>> get Brothers' OR sisters Parteners <<<<<<<<<<<<<<<<
def get_brothers_wives(person_id):
    brothers = get_brothers(person_id,True)
    if not brothers:
        return []
    else:
        brothers.pop(brothers.index(int(person_id)))
        brothers_wives = []
        for brother in brothers:
            brothers_wives += get_parteners(brother)
        return brothers_wives


def get_sisters_husbands(person_id):
    sisters = get_sisters(person_id, True)
    if not sisters:
        return []
    else:
        sisters.pop(sisters.index(int(person_id)))
        sisters_husbands = []
        for sister in sisters:
            sisters_husbands += get_parteners(sister)

        return sisters_husbands


def get_brothers_or_sisters_parteners(person_id):
    if int(person_id) in get_all_persons():
        result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
        person_gender = result[0]["gender"].decode()

        if person_gender == "male":
            brothers_wives = get_brothers_wives(int(person_id))
            return brothers_wives
        elif person_gender == "female":
            sisters_husbands = get_sisters_husbands(int(person_id))
            return sisters_husbands
    else:
        return []


# >>>>>>>>>>>>>>>> get Brothers' Children <<<<<<<<<<<<<<<<

def get_brothers_children(person_id):
    result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
    person_gender = result[0]["gender"].decode()


    if int(person_id) in get_all_persons():
        if int(person_id) in get_family_members_id():
            if person_gender == "male":
                his_brothers_daughters_list_ofLists = []
                his_sisters_daughters_list_ofLists = []

                his_brothers_daughters = []
                his_sisters_daughters = []

                his_brothers = get_brothers(person_id)
                if not his_brothers:
                    pass
                else:
                    his_brothers.pop(his_brothers.index(int(person_id)))
                    for bro in his_brothers:
                        his_brothers_daughters_list_ofLists.append(get_female_childrens(bro))

                    for daughters_list in his_brothers_daughters_list_ofLists:
                        for daughters in daughters_list:
                            his_brothers_daughters.append(daughters)


                his_sisters = get_sisters(person_id)
                if not his_sisters:
                    pass
                else:
                    for sis in his_sisters:
                        his_sisters_daughters_list_ofLists.append(get_female_childrens(sis))

                    for daughters_list in his_sisters_daughters_list_ofLists:
                        for daughter in daughters_list:
                            his_sisters_daughters.append(daughter)

                all_bro_sis_daughters = his_sisters_daughters + his_brothers_daughters
                return all_bro_sis_daughters

            elif person_gender == "female":
                her_brothers_sons_list_ofLists = []
                her_sisters_sons_list_ofLists = []

                her_brothers_sons = []
                her_sisters_sons = []

                her_brothers = get_brothers(person_id)
                if not her_brothers:
                    pass
                else:
                    for bro in her_brothers:
                        her_brothers_sons_list_ofLists.append(get_male_childrens(bro))

                    for sons_list in her_brothers_sons_list_ofLists:
                        for son in sons_list:
                            her_brothers_sons.append(son)

                her_sisters = get_sisters(person_id)
                if not her_sisters:
                    pass
                else:
                    her_sisters.pop(her_sisters.index(int(person_id)))

                    for sis in her_sisters:
                        her_sisters_sons_list_ofLists.append(get_male_childrens(sis))

                    for sons_list in her_sisters_sons_list_ofLists:
                        for son in sons_list:
                            her_sisters_sons.append(son)


                all_bro_sis_sons = her_sisters_sons + her_brothers_sons
                return all_bro_sis_sons

        elif int(person_id) not in get_family_members_id():
            if person_gender == "male":
                his_brothers_daughters_list_ofLists = []
                his_sisters_daughters_list_ofLists = []

                his_brothers_daughters = []
                his_sisters_daughters = []

                his_brothers = get_brothers(person_id)
                if not his_brothers:
                    pass
                else:
                    his_brothers.pop(his_brothers.index(int(person_id)))
                    for bro in his_brothers:
                        his_brothers_daughters_list_ofLists.append(get_female_childrens(bro))

                    for daughters_list in his_brothers_daughters_list_ofLists:
                        for daughters in daughters_list:
                            his_brothers_daughters.append(daughters)

                his_sisters = get_sisters(person_id)
                if not his_sisters:
                    pass
                else:
                    for sis in his_sisters:
                        his_sisters_daughters_list_ofLists.append(get_female_childrens(sis))

                    for daughters_list in his_sisters_daughters_list_ofLists:
                        for daughter in daughters_list:
                            his_sisters_daughters.append(daughter)

                all_bro_sis_daughters = his_sisters_daughters + his_brothers_daughters
                return all_bro_sis_daughters

            elif person_gender == "female":
                her_brothers_sons_list_ofLists = []
                her_sisters_sons_list_ofLists = []

                her_brothers_sons = []
                her_sisters_sons = []

                her_brothers = get_brothers(person_id)


                if not her_brothers:
                    pass
                else:
                    for bro in her_brothers:
                        her_brothers_sons_list_ofLists.append(get_male_childrens(bro))

                    for sons_list in her_brothers_sons_list_ofLists:
                        for son in sons_list:
                            her_brothers_sons.append(son)

                her_sisters = get_sisters(person_id)
                if not her_sisters:
                    pass
                else:
                    her_sisters.pop(her_sisters.index(int(person_id)))
                    for sis in her_sisters:
                        her_sisters_sons_list_ofLists.append(get_male_childrens(sis))

                    for sons_list in her_sisters_sons_list_ofLists:
                        for son in sons_list:
                            her_sisters_sons.append(son)

                all_bro_sis_sons = her_sisters_sons + her_brothers_sons
                return all_bro_sis_sons


# def get_all_parents_and_childrens_family():
#     family_members = get_family_members_id()
#     parent_childs_listOFdic = []
#     for id in family_members:
#         dict_ = {}
#         sql_child = F"""
#                 select familyMember_id from familyMembers where father_id = {id}
#             """
#         result = [id["familyMember_id"] for id in excute_sql(sql_child)]
#         if not result:
#             sql_child = F"""
#                                 select person_id from non_family_members where mother_id = {id}
#                             """
#             result = [id["person_id"] for id in excute_sql(sql_child)]
#
#         dict_[id] = result
#         parent_childs_listOFdic.append(dict_)
#     print(parent_childs_listOFdic)
#     return parent_childs_listOFdic


# def get_all_bro_sis_child(person_id):
#     all_bro_sis = brothers_or_sisters(person_id,True)
#     print(all_bro_sis,">>>>>>>>>>>>>>>.")
#     parents_childs = get_all_parents_and_childrens_family()
#
#     last_bro_sis_childs = []
#
#     keys = []
#     for dicts in parents_childs:
#         keys.append(int(str(dicts.keys())[11:-2]))
#
#     intrsect = list(set(keys) & set(all_bro_sis))
#
#     for dicts_ in parents_childs:
#         key = int(str(dicts_.keys())[11:-2])
#         if key in intrsect:
#             for id in dicts_[key]:
#                 last_bro_sis_childs.append(id)



# >>>>>>>>>>>>>>>> get Step parents  <<<<<<<<<<<<<<<<

def step_parents(person_id):
    if int(person_id) in get_all_persons():
        result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
        person_gender = result[0]["gender"].decode()

        if int(person_id) in get_family_members_id():
            if person_gender == "male":
                try:
                    mother_id = get_mother(person_id)[0]
                    father_id = get_father(person_id)[0]

                    father_wives = get_parteners(father_id)
                    if father_wives:
                        father_wives.pop(father_wives.index(int(mother_id)))
                    return father_wives
                except:
                    return []

            elif person_gender == "female":
                try:
                    father_id = get_father(person_id)[0]
                    mother_id = get_mother(person_id)[0]
                    mother_husbands = get_parteners(mother_id)
                    if mother_husbands:
                        mother_husbands.pop(mother_husbands.index(int(father_id)))
                    return mother_husbands
                except:
                    return []

        elif int(person_id) in get_non_family_members_id():
            if person_gender == "male":
                try:
                    mother_id = get_mother(person_id)[0]
                    father_id = get_father(person_id)[0]
                    if father_id:
                        father_wives = get_parteners(father_id)
                        if father_wives:
                            father_wives.pop(father_wives.index(int(mother_id)))
                        return father_wives
                    else:
                        return []
                except:
                    return []

            elif person_gender == "female":
                try:
                    father_id = get_father(person_id)[0]
                    mother_id = get_mother(person_id)[0]
                    if mother_id:
                        mother_husbands = get_parteners(mother_id)
                        if mother_husbands:
                            mother_husbands.pop(mother_husbands.index(int(father_id)))
                        return mother_husbands
                    else:
                        return []
                except:
                    return []
    else:
        return []


# >>>>>>>>>>>>>>>> GENERAL FUNCTIONS  <<<<<<<<<<<<<<<
def get_name_filter(request):
    if request.method == "GET":
        name = request.GET.get('name')
        name_filter = request.GET.get('name_filte')

        if name_filter == "Contains":
            sql_query= F"""
                SELECT familyMember_id AS id ,person_name AS name_ FROM familyMembers WHERE person_name LIKE '%{name}%'
                UNION
                SELECT person_id AS id ,fullname AS name_  FROM non_family_members WHERE fullname LIKE '%{name}%'
            
            """
            result = excute_sql(sql_query)
            if result:
                last_result_list = []
                for dict_ in result:
                    result_dict = {}
                    id = dict_["id"]

                    if int(id) in get_family_members_id():
                        father_id = excute_sql(F""" select father_id from familyMembers where familyMember_id = {id}""")[0]["father_id"]
                        if father_id:
                            father_name = excute_sql(F""" select person_name from familyMembers where familyMember_id = {int(father_id)}""")[0]["person_name"].decode()
                        else:
                            father_name = ""

                    elif int(id) in get_non_family_members_id():
                        father_id = excute_sql(F""" select father_id from non_family_members where person_id = {int(id)}""")[0]["father_id"]
                        if father_id:
                            print(id)
                            father_name = excute_sql(F""" select fullname from non_family_members where person_id = {int(father_id)}""")[0]["fullname"].decode()
                            print(father_name)
                        else:
                            father_name = ""

                    last_name = dict_["name_"].decode()+" "+father_name

                    result_dict["id"],result_dict["name"] = id,last_name
                    last_result_list.append(result_dict)
            if not result:
                last_result_list = " NO RESULTS FOUND "

            return JsonResponse(last_result_list,safe=False)

        elif name_filter == "BeginWith":
            sql_query = F"""
                            SELECT familyMember_id AS id ,person_name AS name_ FROM familyMembers WHERE person_name LIKE '{name}%'
                            UNION
                            SELECT person_id AS id ,fullname AS name_ FROM non_family_members WHERE fullname LIKE '{name}%'

                        """
            result = excute_sql(sql_query)
            if result:
                last_result_list = []
                for dict_ in result:
                    result_dict = {}
                    id = dict_["id"]

                    if id in get_family_members_id():
                        father_id = excute_sql(F""" select father_id from familyMembers where familyMember_id = {id}""")[0]["father_id"]
                        if father_id:
                            father_name = excute_sql(F""" select person_name from familyMembers where familyMember_id = {int(father_id)}""")[0]["person_name"].decode()
                        else:
                            father_name = ""

                    elif id in get_non_family_members_id():
                        father_id = excute_sql(F""" select father_id from non_family_members where person_id = {int(id)}""")[0]["father_id"]
                        if father_id:
                            father_name = excute_sql(F""" select fullname from non_family_members where person_id = {int(father_id)}""")[0]["fullname"].decode()
                        else:
                            father_name = ""

                    last_name = dict_["name_"].decode() + " " + father_name

                    result_dict["id"], result_dict["name"] = id, last_name
                    last_result_list.append(result_dict)
            if not result:
                last_result_list = " NO RESULTS FOUND "


            return JsonResponse(last_result_list, safe=False)

        elif name_filter == "EndWith":
            sql_query = F"""
                                        SELECT familyMember_id AS id ,person_name AS name_ FROM familyMembers WHERE person_name LIKE '%{name}'
                                        UNION
                                        SELECT person_id AS id ,fullname AS name_ FROM non_family_members WHERE fullname LIKE '%{name}'

                                    """
            result = excute_sql(sql_query)
            if result:
                last_result_list = []
                for dict_ in result:
                    result_dict = {}
                    id = dict_["id"]

                    if id in get_family_members_id():
                        father_id = \
                        excute_sql(F""" select father_id from familyMembers where familyMember_id = {id}""")[0][
                            "father_id"]
                        if father_id:
                            father_name = excute_sql(
                                F""" select person_name from familyMembers where familyMember_id = {int(father_id)}""")[
                                0]["person_name"].decode()
                        else:
                            father_name = ""

                    elif id in get_non_family_members_id():
                        father_id = \
                        excute_sql(F""" select father_id from non_family_members where person_id = {int(id)}""")[0][
                            "father_id"]
                        if father_id:
                            father_name = excute_sql(
                                F""" select fullname from non_family_members where person_id = {int(father_id)}""")[0][
                                "fullname"].decode()
                        else:
                            father_name = ""

                    last_name = dict_["name_"].decode() + " " + father_name

                    result_dict["id"], result_dict["name"] = id, last_name
                    last_result_list.append(result_dict)
            if not result:
                last_result_list = " NO RESULTS FOUND "

            return JsonResponse(last_result_list,safe=False)


def get_maharem(person_id):
    a = grand_parents(person_id)+get_parents(person_id)
    # print(grand_parents(person_id),"grand_parents(person_id)")
    # print(get_parents(person_id),"get_parents(person_id)")
    grandma.clear()
    grandpa.clear()

    # print("===================================================================")

    b = get_childrens(person_id)+brothers_or_sisters(person_id)
    # print(get_childrens(person_id),"get_childrens(person_id)get_childrens(person_id)")
    # print(brothers_or_sisters(person_id),"brothers_or_sisters(person_id)brothers_or_sisters(person_id)")

    # print("===================================================================")

    c = get_uncles_or_aunts(person_id)+get_childrens_parteners(person_id)
    # print(get_uncles_or_aunts(person_id),"get_uncles_or_aunts(person_id)")
    # print(get_childrens_parteners(person_id),"get_childrens_parteners(person_id)")

    # print("===================================================================")

    d = get_partener_parents(person_id)+get_brothers_or_sisters_parteners(person_id)
    # print(get_partener_parents(person_id),"get_partener_parents(person_id)")
    # print(get_brothers_or_sisters_parteners(person_id),"get_brothers_or_sisters_parteners(person_id)")

    # print("===================================================================")

    e = get_brothers_children(person_id)+step_parents(person_id)

    # print(step_parents(person_id),"step_parents(person_id)")

    all_maharem = a+b+c+d+e

    return list(set(all_maharem))


def search_all_family_member(age,gender,operation,status):
    search_query = F"""
                    Select fm.familyMember_id
                    from familyMembers fm 
                    INNER JOIN Person p 
                    ON fm.familyMember_id = p.national_id 
                        WHERE fm.current_status= '{status}' AND p.gender = '{gender}' 
                                AND YEAR(CURRENT_DATE())-YEAR(p.birth_date) {operation} {age}
    """
    result = excute_sql(search_query)
    last_result = []
    for id in result:
        last_result.append(id["familyMember_id"])
    return list(set(last_result))


def get_all_available_family_member(person_id,age,gender,operation,status):
    result = excute_sql(F"SELECT gender FROM Person WHERE national_id = {person_id}")
    person_gender = result[0]["gender"].decode()


    if gender == person_gender:
        return []
    else:
        all_maharem = get_maharem(person_id)

        specific_family_member = search_all_family_member(age,gender,operation,status)

        intersect = set(all_maharem) & set(specific_family_member)
        intersect_list = [i for i in intersect]

        for i in intersect_list:
            specific_family_member.pop(specific_family_member.index(int(i)))

    return specific_family_member


def get_person_data(specific_family_member):
    last_persons_info_list = {}
    for person_id in specific_family_member:
        person_info = {}
        if int(person_id) in get_family_members_id():
            person_data = F'''
                    Select fm.person_name,fm.current_status,YEAR(CURRENT_DATE())-YEAR(p.birth_date),p.gender,fm.familyMember_id
                    from familyMembers fm 
                    INNER JOIN Person p 
                    ON fm.familyMember_id = p.national_id 
                        where p.national_id = {int(person_id)}

            '''
            is_dead = excute_sql(F" SELECT death_date from Person WHERE national_id = {int(person_id)}")[0]["death_date"]

            if not is_dead:
                result = excute_sql(person_data)
                age = result[0]["YEAR(CURRENT_DATE())-YEAR(p.birth_date)"]
                if age >= 18:
                    id = result[0]["familyMember_id"]
                    name = result[0]["person_name"].decode()
                    status = result[0]["current_status"].decode()
                    gender = result[0]["gender"].decode()
                    person_info["id"],person_info["name"], person_info["status"], person_info["age"], person_info["gender"] = int(id),name, status, age, gender
                    last_persons_info_list[id] = person_info
                else:
                    continue

            else:
                continue

        elif int(person_id) in get_non_family_members_id():
            person_data = F'''
                                Select nfm.fullname,nfm.current_status,YEAR(CURRENT_DATE())-YEAR(p.birth_date),p.gender,nfm.person_id
                                from non_family_members nfm 
                                INNER JOIN Person p 
                                ON nfm.person_id = p.national_id 
                                    where p.national_id = {int(person_id)}

                        '''
            is_dead = excute_sql(F" SELECT death_date from Person WHERE national_id = {int(person_id)}")[0]["death_date"]
            if not is_dead:
                result = excute_sql(person_data)
                id = str(result[0][4])
                name = str(result[0][0])[11:][:-1]
                status = str(result[0][1])[11:][:-1]
                age = int(str(result[0][2]))
                gender = str(result[0][3])[11:][:-1]
                person_info["name"], person_info["status"], person_info["age"], person_info["gender"] = name[1:-1], status[1:-1], age, gender[1:-1]
                last_persons_info_list[id] = person_info
            else:
                continue

    return last_persons_info_list


# >>>>>>>>>>>>>>>> CALL SERACH <<<<<<<<<<<<<<<<

def render_search(request):
    return render(request,"search.html")


def get_data_from_search_form(request):
    if request.method == 'POST':
        age = request.POST.get('age')
        operation = request.POST.get('operation')
        gender = request.POST.get('gender')
        status = request.POST.get('status')
        person_id = request.POST.get("person_id")

        death_date = excute_sql(F""" select death_date from Person where national_id = {int(person_id)}""")[0]["death_date"]
        if death_date:
            return HttpResponse("THIS Person Is DEAD !")

        else:
            get_all_available = get_all_available_family_member(person_id, age, gender, operation, status)

            persons_info_list = get_person_data(get_all_available)

            if not persons_info_list:
                response = str("NO Parteners Found")
                return HttpResponse(response)

            return JsonResponse(persons_info_list)
    else:
        return JsonResponse({})



def show_profile(request,id):
    print(id,"()()()()()()()()()()")
    return render(request,'profile.html')

# >>>>>>>>>>>>>>>> CALL DATA ENTRY <<<<<<<<<<<<<<<<

def render_data_entry(request):
    return render(request, "data_entry.html")

def their_children(person_id):
    last_partener_data_list = []
    person_childrens = get_childrens(int(person_id),all=True)
    parteners = get_parteners(int(person_id))
    for partener in parteners:
        partener_dict = {}

        if int(partener) in get_family_members_id():
            partener_name = excute_sql(F""" select person_name from familyMembers where familyMember_id = {int(partener)}""")[0]["person_name"].decode()

        elif int(partener) not in get_family_members_id():
            partener_name = excute_sql(F""" select fullname from non_family_members where person_id = {int(partener)}""")[0]["fullname"].decode()


        partener_childrens = get_childrens(int(partener),all=True)
        thier_children_list = list(set(person_childrens) & set(partener_childrens))

        partener_dict[partener_name] = thier_children_list
        last_partener_data_list.append(partener_dict)
    return last_partener_data_list

def get_data_from_entry_form(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        national_id = data["national_id"]
        first_name = data['f_name']
        birthdate = data['birthdate']
        birthdate = str(birthdate[6:10] + '-' + birthdate[3:5] + '-' + birthdate[0:2])
        gender = data['gender']
        father = data['father']
        mother = data['mother']


        if int(father) in get_family_members_id():
            father_name = excute_sql(F""" select person_name from familyMembers where familyMember_id = {int(father)}""")[0]["person_name"].decode()

        elif int(father) not in get_family_members_id():
            father_name = excute_sql(F""" select fullname from non_family_members where person_id = {int(father)}""")[0]["fullname"].decode()

        try:
            death_date = data['dead_date']
            death_date = str(death_date[6:10] + '-' + death_date[3:5] + '-' + death_date[0:2])

            death_datetime = datetime.strptime(death_date,"%Y-%m-%d")
            birth_datetime = datetime.strptime(birthdate,"%Y-%m-%d")
            print(death_datetime,"    ",birth_datetime)
            print(death_datetime < birth_datetime)

            if death_datetime < birth_datetime:
                print("INVALID DEATH OR BIRTH DATE")
                return HttpResponse("INVALID DEATH OR BIRTH DATE")
            else:
                try:
                    father_is_family = data['is_family']
                except:
                    father_is_family = None
        except:
            try:
                death_date = "NULL"
                father_is_family = data['is_family']
            except:
                death_date = "NULL"
                father_is_family = None


        if death_date == "NULL":
            insert_into_person = F"""
                    INSERT INTO Person(national_id,birth_date,death_date,gender) VALUES ({int(national_id)},'{birthdate}',{death_date},'{gender}')
            """
        elif death_date != "NULL":
            insert_into_person = F"""
                                INSERT INTO Person(national_id,birth_date,death_date,gender) VALUES ({int(national_id)},'{birthdate}','{death_date}','{gender}')
                        """

        mycursor.execute(insert_into_person)
        mydb.commit()

        # last_record_query = excute_sql(F""" SELECT national_id FROM Person ORDER BY national_id DESC LIMIT 1 """)[0]["national_id"]

        age = int(excute_sql(
            F""" select YEAR(CURRENT_DATE())-YEAR(birth_date) AS age from Person where national_id = {int(national_id)}""")[0]['age'])

        if father_is_family:
            insert_into_family = F""" INSERT INTO familyMembers(familyMember_id,person_name,family_id,family_name,father_id,mother_id,current_status) 
                                        VALUES ({int(national_id)},'{first_name+" "+father_name}',1,"Saif Elyazel",{father},{mother},NULL)
            
            """
            mycursor.execute(insert_into_family)
            mydb.commit()

        if not father_is_family:
            insert_into_non_family = F""" INSERT INTO non_family_members(person_id,fullname,father_id,mother_id,current_status) 
                                            VALUES ({int(national_id)},'{first_name+" "+father_name}',{father},{mother},NULL)
            """
            mycursor.execute(insert_into_non_family)
            mydb.commit()


        return HttpResponse("DONE")

# >>>>>>>>>>>>>>>>>>>>>>>>>>> PROFILE <<<<<<<<<<<<<<<<<<<<<<<
# def show_profile(request,person_id):
#     if int(person_id) in get_family_members_id():
#         name =


# >>>>>>>>>>>>>>>>>>>>>>>>>>> PROFILE <<<<<<<<<<<<<<<<<<<<<<<

# >>>>>>>>>>>>>>>> JSON PERSON/FAMILY/NON-FAMILY DATA  <<<<<<<<<<<<<<<<
# all_persons male
def get_all_persons_key():
    sql = F" SELECT national_id FROM Person"
    result = excute_sql(sql)
    person_id_list = []
    for record in result:
        person_id_list.append(record['national_id'])
    return person_id_list

def get_family_members_id_key():
    sql = F" SELECT familyMember_id FROM familyMembers"
    result = excute_sql(sql)
    family_members_id_list = []
    for record in result:
        family_members_id_list.append(record['familyMember_id'])
    return family_members_id_list

def get_non_family_members_id_key():
    sql = F" SELECT person_id FROM non_family_members"
    result = excute_sql(sql)
    non_family_members_id_list = []
    for record in result:
        non_family_members_id_list .append(record['person_id'])
    return non_family_members_id_list


def get_all_person_male(request):
    if request.method == "GET":
        all_person = get_all_persons_key()
        all_male_person = []
        all_male_person_data = []
        for person in all_person:
            result = excute_sql(F" SELECT gender FROM Person WHERE national_id = {int(person)}")
            person_gender = result[0]['gender'].decode()
            if person_gender == "male":
                all_male_person.append(person)
        for male in all_male_person:
            male_data = {}
            if male in get_family_members_id_key():
                name_result = excute_sql(F" select person_name from familyMembers where familyMember_id = {int(male)}")[0]
                name = str(str(name_result)[12:-3])[16:]
                male_data["id"] = int(male)
                male_data["name"] = name
                male_data["isFM"] = True
                all_male_person_data.append(male_data)
            elif male in get_non_family_members_id_key():
                name_result = excute_sql(F" select fullname from non_family_members where person_id = {int(male)}")[0]
                name = str(str(name_result)[14:-3])[11:]
                male_data["id"] = int(male)
                male_data["name"] = name
                male_data["isFM"] = False
                all_male_person_data.append(male_data)
        return JsonResponse(all_male_person_data,safe=False)
    else:
        return HttpResponse("POST REQUEST")

# all person female
def get_all_person_female(request):
    if request.method == "GET":
        person_id = request.GET.get("husband_id")

        family_members_id = get_family_members_id()

        if int(person_id) in family_members_id:
            query = F'''
                        select current_status from familyMembers where familyMember_id = {int(person_id)}
                    '''
            my_result = excute_sql(query)[0]["current_status"].decode()
            if my_result == "single":
                return JsonResponse([],safe=False)

            else:
                wives_id = []
                sql_wives_ids = F"""
                                                        SELECT partener_id FROM familyMember_marriage
                                                                WHERE familyMember_id = {int(person_id)}
                                    """
                if not sql_wives_ids:
                    sql_wives_ids = F"""
                                                                        SELECT familyMember_id FROM familyMember_marriage
                                                                                WHERE partener_id = {int(person_id)}
                                                    """
                    wives_id += [id["familyMember_id"] for id in excute_sql(sql_wives_ids)]
                else:
                    wives_id += [id["partener_id"] for id in excute_sql(sql_wives_ids)]


                wives_ids_list = []
                for record in wives_id:
                    wives_ids_list.append(record)


        else:
            sql_wives_ids = F"""
                                                    SELECT familyMember_id FROM familyMember_marriage
                                                            WHERE partener_id = {int(person_id)}
                                """
            wives_id = [id["familyMember_id"] for id in excute_sql(sql_wives_ids)]

            wives_ids_list = []
            for record in wives_id:
                wives_ids_list.append(record)

        if wives_ids_list == []:
            return HttpResponse("NO PARTENERS")
        else:
            all_female_person_data = []
            for female in wives_ids_list:
                female_data = {}
                if int(female) in get_family_members_id_key():
                    name_result = \
                    excute_sql(F" select person_name from familyMembers where familyMember_id = {int(female)}")[0]
                    name = str(str(name_result)[12:-3])[16:]

                    female_data["id"] = int(female)
                    female_data["name"] = name
                    female_data["isFM"] = True
                    all_female_person_data.append(female_data)
                elif int(female) in get_non_family_members_id_key():
                    name_result = \
                    excute_sql(F" select fullname from non_family_members where person_id = {int(female)}")[0]
                    name = str(str(name_result)[14:-3])[11:]

                    female_data["id"] = int(female)
                    female_data["name"] = name
                    female_data["isFM"] = False
                    all_female_person_data.append(female_data)

            return JsonResponse(all_female_person_data,safe=False)

def last_fill_select(request,gender):
    if request.method == "GET":
        if gender == 'male':
            all_person = get_all_persons_key()
            all_male_person = []
            all_male_person_data = []
            for person in all_person:
                result = excute_sql(F" SELECT gender FROM Person WHERE national_id = {int(person)}")
                person_gender = result[0]['gender'].decode()
                if person_gender == "male":
                    all_male_person.append(person)
            for male in all_male_person:
                male_data = {}
                if male in get_family_members_id_key():
                    name_result = excute_sql(F" select person_name from familyMembers where familyMember_id = {int(male)}")[0]
                    name = str(str(name_result)[12:-3])[16:]
                    male_data["id"] = int(male)
                    male_data["name"] = name
                    male_data["isFM"] = True
                    all_male_person_data.append(male_data)
                elif male in get_non_family_members_id_key():
                    name_result = excute_sql(F" select fullname from non_family_members where person_id = {int(male)}")[
                        0]
                    name = str(str(name_result)[14:-3])[11:]
                    male_data["id"] = int(male)
                    male_data["name"] = name
                    male_data["isFM"] = False
                    all_male_person_data.append(male_data)
            last_return = all_male_person_data


        elif gender == "female":
            all_person = get_all_persons_key()
            all_female_person = []
            all_female_person_data = []
            for person in all_person:
                result = excute_sql(F" SELECT gender FROM Person WHERE national_id = {int(person)}")
                person_gender = result[0]['gender'].decode()
                if person_gender == "female":
                    all_female_person.append(person)

            for female in all_female_person:
                female_data = {}
                if female in get_family_members_id_key():
                    name_result = excute_sql(F" select person_name from familyMembers where familyMember_id = {int(female)}")[0]
                    name = str(str(name_result)[12:-3])[16:]

                    female_data["id"] = int(female)
                    female_data["name"] = name
                    female_data["isFM"] = True
                    all_female_person_data.append(female_data)
                elif female in get_non_family_members_id_key():
                    name_result = excute_sql(F" select fullname from non_family_members where person_id = {int(female)}")[0]
                    name = str(str(name_result)[14:-3])[11:]

                    female_data["id"] = int(female)
                    female_data["name"] = name
                    female_data["isFM"] = False
                    all_female_person_data.append(female_data)

            last_return = all_female_person_data

        return JsonResponse(last_return,safe=False)
    else:
        return HttpResponse("POST REQUEST")

