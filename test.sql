-- MySQL dump 10.13  Distrib 9.2.0, for Win64 (x86_64)
--
-- Host: localhost    Database: test
-- ------------------------------------------------------
-- Server version	9.2.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('bc8f01a82e50');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `id` int NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `bo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  `image` text COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES ('Описание этой книги',25,'Новая книга 1',NULL,'/picture/3eef5634-e286-4f80-a8c0-0889dd5e2a2e.jpg'),('Во второй половине 19 века в морях и океанах на глаза мореплавателям стал попадаться необычный объект — светящийся веретенообразный предмет, превосходящий скоростью и размерами кита. Профессору Аронакс со слугой Конселем и гарпунером Недом Лендом волею случая попадают на борт необыкновенной и единственной в мире подводной лодки «Наутилус». Капитан и экипаж лодки оказались совсем не чудовищами, и герои пережили немало опасных и удивительных приключений, совершив кругосветное путешествие в 20 тысяч лье под водой.',26,'Двадцать тысяч миль под водой',NULL,'/picture/1485ea30-261a-4a0a-98c9-457b91847818.jpg'),('Самыми страшными войнами являются гражданские, когда ненависть зашкаливает все пределы, а попасть в плен может быть страшнее смерти. Именно в такой ситуации оказалась пятерка северян, чье стремление к свободе было сильнее страха погибнуть в плену или при попытке к бегству. Но результат бегства на воздушном шаре оказался непредсказуемым: в результате урагана их занесло на необитаемый остров. Множество приключений и опасностей поджидают их там, но отвага, знания и изобретательность позволят им не только уцелеть, но и обустроить свой быт.',27,'Таинственный остров',NULL,'/picture/9471a38d-fe8b-4a48-9f08-0a5d5313a429.jpg'),('Эксцентричный англичанин Филеас Фогг заключает пари, согласно которому он должен обогнуть земной шар не более чем за 80 дней. В сопровождении своего слуги Паспарту Фогг отправляется в это не имеющее аналогов путешествие, используя всевозможные виды транспорта и преодолевая препятствия, что ставит перед ним сыщик Фикс. При жизни автора этот роман стал его самой продаваемой книгой, в 1874 году по мотивам романа был поставлен спектакль «Вокруг света в восемьдесят дней». Успех романа был столь велик, что даже вызвал волну подражаний.',28,'Вокруг земли в 80 дней',NULL,'/picture/df9ea1c2-219f-4cdb-b417-e16d93f1ef9c.jpg'),('Центральная Африка — один из самых труднодоступных районов земного шара, и экспедиции туда всегда сопряжены с колоссальными трудностями. Английский путешественник доктор Самюэль Фергюсон предлагает поистине революционный метод исследования этих территорий и вместе с двумя спутниками отправляется в путешествие над центральной Африкой на воздушном шаре, желая связать воедино открытия предыдущих экспедиций. Это - первый роман, принесший будущему великому классику широкую известность.',30,'Пять недель на воздушном шаре',NULL,'/picture/1ed6f573-5701-48f6-82bf-bd852c920134.jpg'),('цуйцуйцуйцу',31,'уйцуйцуйц',NULL,'/picture/dcdbbea9-03c4-4369-8ac7-c3444ed4935d.jpg');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contents`
--

DROP TABLE IF EXISTS `contents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contents` (
  `section_id` int NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `text_id` int DEFAULT NULL,
  `books_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `text_id` (`text_id`),
  KEY `section_id` (`section_id`),
  KEY `books_id` (`books_id`),
  CONSTRAINT `contents_ibfk_3` FOREIGN KEY (`text_id`) REFERENCES `textarrays` (`id`),
  CONSTRAINT `contents_ibfk_4` FOREIGN KEY (`section_id`) REFERENCES `sections` (`id`) ON DELETE CASCADE,
  CONSTRAINT `contents_ibfk_5` FOREIGN KEY (`books_id`) REFERENCES `books` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=160 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contents`
--

LOCK TABLES `contents` WRITE;
/*!40000 ALTER TABLE `contents` DISABLE KEYS */;
INSERT INTO `contents` VALUES (43,149,NULL,26),(43,151,NULL,27),(44,153,NULL,28),(45,154,NULL,30),(39,155,84,NULL);
/*!40000 ALTER TABLE `contents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `description` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `color` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES ('qwewqwqeqw','qweqwe','wqeqwe',1),('qweqw','qweqwe','qweqwe',2);
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sections`
--

DROP TABLE IF EXISTS `sections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sections` (
  `title` text COLLATE utf8mb4_general_ci NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sections`
--

LOCK TABLES `sections` WRITE;
/*!40000 ALTER TABLE `sections` DISABLE KEYS */;
INSERT INTO `sections` VALUES ('Введение',39),('Романы',43),('Повести',44),('Сказки',45);
/*!40000 ALTER TABLE `sections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `textarrays`
--

DROP TABLE IF EXISTS `textarrays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `textarrays` (
  `text_data` text COLLATE utf8mb4_general_ci NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `textarrays`
--

LOCK TABLES `textarrays` WRITE;
/*!40000 ALTER TABLE `textarrays` DISABLE KEYS */;
INSERT INTO `textarrays` VALUES ('string',6),('string',7),('string',8),('hello world',9),('2134213421',10),('фывафы',12),('eqweq',44),('fsdfsdf',45),('fsdfdsf',46),('fgdfg',47),('dasdas',48),('qwer',49),('werwer',50),('eqweq',51),('213123',52),('12e1',53),('12313',54),('12312',55),('йцуй',75),('Во второй половине 19 века в морях и океанах на глаза мореплавателям стал попадаться необычный объект — светящийся веретенообразный предмет, превосходящий скоростью и размерами кита. Профессору Аронакс со слугой Конселем и гарпунером Недом Лендом волею случая попадают на борт необыкновенной и единственной в мире подводной лодки «Наутилус». Капитан и экипаж лодки оказались совсем не чудовищами, и герои пережили немало опасных и удивительных приключений, совершив кругосветное путешествие в 20 тысяч лье под водой.',81),('Уже при жизни Жюля Верна о нем и его книгах ходили легенды: одни читатели видели в нем прославленного путешественника, другие утверждали, что он никогда не покидал своего кабинета, третьи считали, что такого человека в реальности не существует и под этим псевдонимом скрывается целое Географическое общество. Книга Жана Жюль-Верна, внука знаменитого писателя, до сих пор является наиболее полной, обстоятельной и тщательно документированной монографией о личной и творческой жизни первого классика научной фантастики.',84);
/*!40000 ALTER TABLE `textarrays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `username` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `hashed_password` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `role` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('123','$2b$12$Tli4kGuhOuVL3fuBB4kT7uykrk1JvhDy0JHt8ZS1cHjFdpxHin.K.','librarian',1),('12','$2b$12$RYOQaptuzBP/325DvTCON.Cj3EvbmCfmbzHxI4zcTHOolHw56.jAu','librarian',2);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-17 12:32:14
