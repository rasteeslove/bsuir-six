alter session set "_ORACLE_SCRIPT"=true; -- with this, I can create user smh

create user rasteeslove identified by whatever;
GRANT CONNECT, RESOURCE, DBA TO rasteeslove;

-- (reconnect as rasteeslove)

select user from dual; -- rasteeslove


-- 1: to create tables for students and groups
create table UniGroup (
    id number,
    name varchar2(10),                        -- group name
    c_val number                              -- number of students in group
);
create table UniStudent (
    id number,
    name varchar2(30),                        -- student name
    group_id number                           -- student's group id
);


-- 2: to create triggers for ensuring uniqueness of id,
-- id autoincrement, and UniGroup.name uniqueness

create or replace trigger UniStudentUniqueId
    before insert or update on UniStudent
    for each row
declare
    custom_exception exception;
    pragma exception_init(custom_exception, -696969);
    cursor UniStudent_id is
        select id from UniStudent;
begin
    for us_id in UniStudent_id
    loop
        if (us_id.id = :new.id) then
            raise_application_error(-696969, 'id should be unique!');
        end if;
    end loop;
end;

create or replace trigger UniGroupUniqueId
    before insert or update on UniGroup
    for each row
declare
    custom_exception exception;
    pragma exception_init(custom_exception, -696969);
    cursor UniGroup_id is
        select id from UniGroup;
begin
    for ug_id in UniGroup_id
    loop
        if (ug_id.id = :new.id) then
            raise_application_error(-696969, 'id should be unique!');
        end if;
    end loop;
end;
