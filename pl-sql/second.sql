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
    pragma exception_init(custom_exception, -20042);
    cursor UniStudent_id is
        select id from UniStudent;
begin
    for us_id in UniStudent_id
    loop
        if (us_id.id = :new.id) then
            raise_application_error(-20042, 'id should be unique!');
        end if;
    end loop;
end;

create or replace trigger UniGroupUniqueId
    before insert or update on UniGroup
    for each row
declare
    custom_exception exception;
    pragma exception_init(custom_exception, -20042);
    cursor UniGroup_id is
        select id from UniGroup;
begin
    for ug_id in UniGroup_id
    loop
        if (ug_id.id = :new.id) then
            raise_application_error(-20042, 'id should be unique!');
        end if;
    end loop;
end;

-- this will produce an error:
begin
    insert into UniGroup(id, name, c_val) values(1, '953501', 0);
    insert into UniGroup(id, name, c_val) values(1, '953505', 0);
end;

-- this won't:
begin
    insert into UniGroup(id, name, c_val) values(1, '953501', 0);
    insert into UniGroup(id, name, c_val) values(5, '953505', 0);
end;

-- this will:
begin
    insert into UniStudent(id, name, group_id) values(42, 'Alice', 1);
    insert into UniStudent(id, name, group_id) values(42, 'Bob', 5);
end;

-- this won't:
begin
    insert into UniStudent(id, name, group_id) values(42, 'Alice', 1);
    insert into UniStudent(id, name, group_id) values(69, 'Bob', 5);
end;

create or replace trigger UniStudentAutoIncrement
    before insert on UniStudent
    for each row
declare
    max_id number := 0;
begin
    select max(id) into max_id from UniStudent;
    if (max_id is null) then
        max_id := 0;
    end if;
    :new.id := max_id + 1;
end;

create or replace trigger UniGroupAutoIncrement
    before insert on UniGroup
    for each row
declare
    max_id number := 0;
begin
    select max(id) into max_id from UniGroup;
    if (max_id is null) then
        max_id := 0;
    end if;
    :new.id := max_id + 1;
end;

begin
    insert into UniGroup(name, c_val) values('953502', 0);
    insert into UniGroup(name, c_val) values('953503', 0);
end;

select * from UniGroup;

begin
    insert into UniStudent(name, group_id) values('Adam', 1);
    insert into UniStudent(name, group_id) values('Eve', 5);
end;

select * from UniStudent;

create or replace trigger UniGroupUniqueName
    before insert or update on UniGroup
    for each row
declare
    custom_exception exception;
    pragma exception_init(custom_exception, -20069);
    cursor UniGroup_name is
        select name from UniGroup;
begin
    for ug_name in UniGroup_name
    loop
        if (ug_name.name = :new.name) then
            raise_application_error(-20069, 'name should be unique!');
        end if;
    end loop;
end;

begin
    insert into UniGroup(name, c_val) values('953501', 10);
end;


-- 3: to code a trigger designed to cascade-delete group's students
-- on group deletion
create or replace trigger UniGroupStudentsCascadeDelete
    before delete on UniGroup
    for each row
begin
    delete from UniStudent where group_id=:old.id;
end;

select * from UniStudent;

delete from UniGroup where id=1;

select * from UniStudent;
