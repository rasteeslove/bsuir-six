-- 1: to create MyTable w columns id number and val number
create table MyTable
     (
         id number primary key,
         val number
     );


-- 2: to code an anon block which writes 10,000 random ints into MyTable
declare
    i number := 0;
    n pls_integer;
begin
    loop
        i := i + 1;
        exit when (i > 10000);
        n := dbms_random.random();
        insert into MyTable (id, val) values (i, n);
    end loop;
end;

select * from MyTable;


-- 3: to code a function which outputs 'true' if there are more
-- even values in MyTable than odd ones, 'false' if there are more
-- odd values, and 'equal' if there are an equal number of both
create function odd_or_even return varchar is
    odd number;
    even number;
begin
    select count(*) into even from MyTable where mod(val, 2)=0;
    select count(*) into odd from MyTable where mod(val, 2)<>0;
    if even > odd then
        return 'true';
    elsif even < odd then
        return 'false';
    else
        return 'equal';
    end if;
end;

-- set serveroutput on I guess, but I use DataGrip so no need

begin
    dbms_output.put_line(odd_or_even());
end;


-- 4: to code a function which gets id and outputs pl sql code to
-- run to insert the row of the specified id
create or replace function id_search(row_id in number) return varchar is
    row_val number;
    rand pls_integer;
begin
    select val into row_val from MyTable where id=row_id;
    return 'insert into MyTable(id, val) values ('
               || row_id || ', ' || row_val || ');';
        exception
        when no_data_found then
            select dbms_random.random into rand from dual;
            return 'insert into MyTable(id, val) values ('
                       || row_id || ', ' || rand || ');';
end;

begin
    dbms_output.put_line(id_search(2));
    dbms_output.put_line(id_search(-1));
end;


-- 5: to code procedures implementing DML operations for MyTable
-- (insert, update, delete)
create or replace procedure my_insert(insert_val in number) is
    rows_num number;
begin
    select count(*) into rows_num from MyTable;
    insert into MyTable(id, val) values (rows_num+1, insert_val);
        exception
            when others then
                dbms_output.put_line('error in my_insert');
end my_insert;

begin
    my_insert(69);
end;

select * from MyTable where id>9990;

create or replace procedure my_update(row_id in number, new_val in number) is
begin
    update MyTable set val = new_val where id=row_id;
        exception
            when others then
                dbms_output.put_line('error in my_update');
end;

begin
    my_update(3, 42);
end;

select * from MyTable where id< 10;

create or replace procedure my_delete(row_id in number) is
begin
    delete from MyTable where row_id=id;
        exception
            when others then
                dbms_output.put_line('error in my_delete');
end;

begin
    my_delete(2112);
end;

select * from MyTable where id>2100 and id<2120;


-- 6: to code a function which calculates yearly salary based on
-- the monthly salary and the annual bonus percentage or whatever.
-- answer = monthly salary * 12 * (1 + bonus/100)
-- the percentage to be submitted as an integer
-- bad input to be intercepted
create or replace function yearly_salary(monthly in real, bonus in number) return float is
    float_bonus float := 0;
begin
    if monthly<0 or bonus<0 or bonus>100 then
        dbms_output.put_line('invalid input values');
        return -1;
    end if;
    float_bonus := bonus/100;
    return (1+float_bonus) * monthly * 12;
        exception
            when others then
                dbms_output.put_line('error in yearly_salary');
                return -1;
end;

begin
    dbms_output.put_line(yearly_salary(500, 1));
    dbms_output.put_line(yearly_salary(1000, -5));
    dbms_output.put_line(yearly_salary(1000, 5));
    dbms_output.put_line(yearly_salary(-25000, 20));
    dbms_output.put_line(yearly_salary(25000, 20));
end;
