drop trigger if exists before_enter_class;
DELIMITER $$

create trigger before_enter_class after update
on class_room for each row
begin
	declare new_size int;
    set new_size = (select total
						from class_room
                        where new.id = id);
	if new_size >= 5 then
		signal sqlstate '45001' set message_text = "Vuot qua so luong toi da";
    end if;
end
$$