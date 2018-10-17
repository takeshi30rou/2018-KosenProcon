<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<title>add_user</title>
</head>
<body>
	<?php
	if(isset($_POST["last"])){
		$last = $_POST["last"];
		$last_kana = $_POST["last_kana"];
		$first = $_POST["first"];
		$first_kana = $_POST["first_kana"];

		if (! file_exists ( 'upload' )) {
			mkdir ( 'upload' );
		}
		$json = "{\"last\":\"".$last."\",\"first\":\"".$first."\",\"last_kana\":\"".$last_kana."\",\"first_kana\":\"".$first_kana."\"}";

		file_put_contents("upload/target_info.json", $json);

		if(is_uploaded_file ( $_FILES ['image1'] ['tmp_name'])){
			if(is_uploaded_file ( $_FILES ['image2'] ['tmp_name'])){
				if(is_uploaded_file ( $_FILES ['image3'] ['tmp_name'])){
					move_uploaded_file ( $_FILES ['image1'] ['tmp_name'], "upload/1.jpg");
					move_uploaded_file ( $_FILES ['image2'] ['tmp_name'], "upload/2.jpg");
					move_uploaded_file ( $_FILES ['image3'] ['tmp_name'], "upload/3.jpg");
					die("アップロードが完了しました。しばらくお待ち下さい");
					echo "<meta http-equiv='refresh' content='2;URL=http://kyo.local:1880/add'>";
				}else{
					echo "内部でエラーが発生しました。やり直してください";
				}

			}else{
				echo "内部でエラーが発生しました。やり直してください";
			}
		}else{
			echo "内部でエラーが発生しました。やり直してください";
		}	
	}else{
		echo "直接アクセスしてます";
	}

	?>
</body>
</html>