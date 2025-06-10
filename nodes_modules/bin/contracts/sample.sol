pragma solidity >= 0.5.0 < 0.7.0;
contract LandRegistration{
 
struct posts{

 
	uint post_id;
	uint owner_id;
	uint category_id;
	string title;
	string description;
	string date_time;
	string place;
	string latitude;
	string longitude;
	string status;


}

struct transaction{

 
	uint transaction_id;
	uint post_id;
	uint owner_id;
	uint user_id;
	uint appointment_id;
	string datetime;
	string status;


}

posts []fu;

transaction []tu;



function add_posts(uint post_id,
	uint owner_id,uint category_id,
	
	string memory title,string memory description,string memory date_time,string memory place,string memory latitude,string memory longitude,
	string memory status)
	public
	{
	posts memory f1=posts(post_id,owner_id,category_id,title,description,date_time,place,latitude,longitude,status);
	fu.push(f1);
	}




function add_transaction(uint transaction_id,
	uint post_id,uint owner_id,uint user_id,uint appointment_id,
	
	string memory datetime,
	string memory status)
	public
	{
	transaction memory f2=transaction(transaction_id,post_id,owner_id,user_id,appointment_id,datetime,status);
	tu.push(f2);

	
	}


}

