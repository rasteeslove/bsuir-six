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

-- some initial data:
begin
    insert into UniGroup(id, name, c_val) values(1, '953501', 0);
    insert into UniGroup(id, name, c_val) values(2, '953502', 0);
    insert into UniGroup(id, name, c_val) values(3, '953503', 0);

    insert into UniStudent(id, name, group_id) values(11, 'A', 1);
    insert into UniStudent(id, name, group_id) values(12, 'B', 1);
    insert into UniStudent(id, name, group_id) values(13, 'C', 2);
    insert into UniStudent(id, name, group_id) values(14, 'D', 2);
    insert into UniStudent(id, name, group_id) values(15, 'E', 3);
    insert into UniStudent(id, name, group_id) values(16, 'F', 3);
end;

select * from UniGroup;
select * from UniStudent;

-- 2: to create triggers for ensuring uniqueness of id,
-- id autoincrement, and UniGroup.name uniqueness

create or replace trigger UniStudentUniqueId
    before insert on UniStudent -- note: this also should be for update
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

-- drop trigger UniStudentUniqueId;

create or replace trigger UniGroupUniqueId
    before insert on UniGroup -- note: this also should be for update
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

-- drop trigger UniGroupUniqueId;

-- this will produce an error:
begin
    insert into UniGroup(id, name, c_val) values(5, '953504', 0);
    insert into UniGroup(id, name, c_val) values(5, '953505', 0);
end;

-- this won't:
begin
    insert into UniGroup(id, name, c_val) values(4, '953504', 0);
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
    if :new.id is null then
        :new.id := max_id + 1;
    end if;
end;

-- drop trigger UniStudentAutoIncrement;

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
    if :new.id is null then
        :new.id := max_id + 1;
    end if;
end;

-- drop trigger UniGroupAutoIncrement;

begin
    insert into UniGroup(name, c_val) values('953506', 0);
    insert into UniGroup(name, c_val) values('953507', 0);
end;

select * from UniGroup;

begin
    insert into UniStudent(name, group_id) values('Adam', 1);
    insert into UniStudent(name, group_id) values('Eve', 5);
end;

select * from UniStudent;

create or replace trigger UniGroupUniqueName
    before insert on UniGroup -- note: this also should be for update
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

-- drop trigger UniGroupUniqueName;

-- this will produce an error:
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

-- drop trigger UniGroupStudentsCascadeDelete;

select * from UniStudent;

delete from UniGroup where id=1;

select * from UniStudent;

-- 4: to code a trigger design to journal all actions
-- on UniStudent table

create table UniStudentLog (
    old_id number,
    new_id number,
    old_name varchar2(30),
    new_name varchar2(30),
    old_group_id number,
    new_group_id number,
    operation varchar2(10),
    time timestamp
);

create or replace trigger UniStudentLogging
    after update or insert or delete on UniStudent -- 'after' bc id autoincrement doesn't work w 'before'
    for each row
begin
    if inserting then
        insert into UniStudentLog(new_id, new_name, new_group_id,
                                  operation, time)
            values(:new.id, :new.name, :new.group_id,
                   'INSERT', current_timestamp);
    elsif updating then
        insert into UniStudentLog(old_id, new_id,
                                  old_name, new_name,
                                  old_group_id, new_group_id,
                                  operation, time)
            values(:old.id, :new.id,
                   :old.name, :new.name,
                   :old.group_id, :new.group_id,
                   'UPDATE', current_timestamp);
    elsif deleting then
        insert into UniStudentLog(old_id, old_name, old_group_id,
                                  operation, time)
            values(:old.id, :old.name, :old.group_id,
                   'DELETE', current_timestamp);
    end if;
end;

-- drop trigger UniStudentLogging;

begin
    insert into UniGroup(id, name, c_val) values(1, '953501', 0);
end;

begin
    insert into UniStudent(name, group_id) values('Biba', 1);
    insert into UniStudent(name, group_id) values('Boba', 5);
end;

begin
    update UniStudent set group_id=5 where name='Biba';
    update UniStudent set group_id=1 where name='Boba';
end;

begin
    delete from UniStudent where name='Biba' or name='Boba';
end;

begin
    delete from UniGroup where id=2;
end;

select * from UniStudentLog;

-- 5: to code a procedure designed to restoring the UniStudent table
-- to its state as of *some timestamp* based on the previous task

create or replace procedure UniStudentRestore(restore_time in timestamp) is
begin
    for log_entry in (
        select * from UniStudentLog
            where time > restore_time
            order by time desc
        )
    loop
        case log_entry.operation
            when 'UPDATE' then
                update UniStudent set
                    id = log_entry.old_id,
                    name = log_entry.old_name,
                    group_id = log_entry.old_group_id
                where id=log_entry.new_id;
            when 'INSERT' then
                delete from UniStudent where id=log_entry.new_id;
            when 'DELETE' then
                insert into UniStudent(id, name, group_id) values(
                    log_entry.old_id,
                    log_entry.old_name,
                    log_entry.old_group_id
                );
        end case;
    end loop;
end;

select * from UniStudent;

begin
    UniStudentRestore(to_timestamp('2022/04/05 13:07:30', 'YYYY/MM/DD HH24:MI:SS'));
end;

select * from UniStudent;

-- 6: to code a trigger which changes c_val in UniGroup
-- on UniStudent changes

truncate table UniStudent;
truncate table UniGroup;

create or replace trigger UniGroupCValUpdater
    before update or insert or delete on UniStudent
    for each row
begin
    if inserting then
        update UniGroup set c_val=c_val+1
            where id=:new.group_id;
    elsif updating then
        if :new.group_id <> :old.group_id then
            update UniGroup set c_val=c_val-1
                where id=:old.group_id;
            update UniGroup set c_val=c_val+1
                where id=:new.group_id;
        end if;
    elsif deleting then
        update UniGroup set c_val=c_val-1
            where id=:old.group_id;
    end if;
end;

select * from UniStudent;
select * from UniGroup;


begin
    insert into UniGroup(id, name, c_val) values(1, '953501', 0);
    insert into UniGroup(id, name, c_val) values(2, '953502', 0);
    insert into UniGroup(id, name, c_val) values(3, '953503', 0);

    insert into UniStudent(name, group_id) values('A', 1);
    insert into UniStudent(name, group_id) values('B', 1);
    insert into UniStudent(name, group_id) values('C', 2);
    insert into UniStudent(name, group_id) values('D', 2);
    insert into UniStudent(name, group_id) values('E', 3);
    insert into UniStudent(name, group_id) values('F', 3);
    insert into UniStudent(name, group_id) values('G', 1);
    insert into UniStudent(name, group_id) values('H', 1);
    insert into UniStudent(name, group_id) values('I', 1);
    insert into UniStudent(name, group_id) values('J', 2);
    insert into UniStudent(name, group_id) values('K', 2);
    insert into UniStudent(name, group_id) values('L', 3);
end;

select * from UniGroup;

begin
    update UniStudent set group_id=3 where name='J';
end;

select * from UniGroup;

delete from UniStudent where name='A' or name='G' or name='I';

select * from UniGroup;
