-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jun 14, 2026 at 05:27 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `rehab_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `chat_notes`
--

CREATE TABLE `chat_notes` (
  `id` int(11) NOT NULL,
  `session_id` int(11) DEFAULT NULL,
  `patient_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `tag` enum('manual','session','event','alert') DEFAULT 'manual',
  `message` text NOT NULL,
  `snapshot_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`snapshot_data`)),
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `encoder_data`
--

CREATE TABLE `encoder_data` (
  `id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  `timestamp_s` float NOT NULL,
  `angle_deg` float NOT NULL,
  `recorded_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `loadcell_data`
--

CREATE TABLE `loadcell_data` (
  `id` int(11) NOT NULL,
  `session_id` int(11) NOT NULL,
  `timestamp_s` float NOT NULL,
  `force1_N` float NOT NULL,
  `force2_N` float NOT NULL,
  `recorded_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` enum('session_done','alert','message','system') DEFAULT 'message',
  `title` varchar(200) NOT NULL,
  `body` text DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `link` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `patients`
--

CREATE TABLE `patients` (
  `id` int(11) NOT NULL,
  `code` varchar(20) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `birth_year` int(11) DEFAULT NULL,
  `gender` enum('male','female','other') DEFAULT NULL,
  `diagnosis` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `patients`
--

INSERT INTO `patients` (`id`, `code`, `full_name`, `birth_year`, `gender`, `diagnosis`, `notes`, `assigned_to`, `created_at`) VALUES
(1, 'BN001', 'ĐÀO CÔNG KHÔI', 2006, 'male', 'Phục hồi chức năng sau phẫu thuật khớp gối', 'Theo dõi sát biên độ góc và lực tì chân', 1, '2026-06-10 20:45:09'),
(2, 'BN002', 'NGUYỄN CHU HIẾU', 2006, 'female', 'Yếu cơ chân sau tai biến', 'Tập các bài tập tăng cường lực cơ đùi', 1, '2026-06-10 20:45:09');

-- --------------------------------------------------------

--
-- Table structure for table `sessions`
--

CREATE TABLE `sessions` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `started_at` datetime DEFAULT current_timestamp(),
  `ended_at` datetime DEFAULT NULL,
  `status` enum('active','completed','interrupted') DEFAULT 'active',
  `total_deg` float DEFAULT NULL,
  `duration_s` float DEFAULT NULL,
  `avg_velocity` float DEFAULT NULL,
  `max_force1` float DEFAULT NULL,
  `max_force2` float DEFAULT NULL,
  `summary_note` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `sessions`
--

INSERT INTO `sessions` (`id`, `patient_id`, `user_id`, `started_at`, `ended_at`, `status`, `total_deg`, `duration_s`, `avg_velocity`, `max_force1`, `max_force2`, `summary_note`) VALUES
(1, 1, 1, '2026-06-10 21:09:05', NULL, 'active', NULL, NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `full_name` varchar(100) DEFAULT NULL,
  `role` enum('admin','therapist','viewer') DEFAULT 'therapist',
  `is_active` tinyint(1) DEFAULT 1,
  `notify_email` tinyint(1) DEFAULT 1,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `email`, `full_name`, `role`, `is_active`, `notify_email`, `created_at`) VALUES
(1, 'admin', '$2b$12$6rYgK79l1uP5R9XfG9G4e.p7O9vYdE3BvZvY1gKz5W8d6M7vK9vX.', NULL, 'Bác sĩ Quản trị', 'admin', 1, 1, '2026-06-10 20:35:18');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `chat_notes`
--
ALTER TABLE `chat_notes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `encoder_data`
--
ALTER TABLE `encoder_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `loadcell_data`
--
ALTER TABLE `loadcell_data`
  ADD PRIMARY KEY (`id`),
  ADD KEY `session_id` (`session_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `patients`
--
ALTER TABLE `patients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `code` (`code`),
  ADD KEY `assigned_to` (`assigned_to`);

--
-- Indexes for table `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `patient_id` (`patient_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `chat_notes`
--
ALTER TABLE `chat_notes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `encoder_data`
--
ALTER TABLE `encoder_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `loadcell_data`
--
ALTER TABLE `loadcell_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `patients`
--
ALTER TABLE `patients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `sessions`
--
ALTER TABLE `sessions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `chat_notes`
--
ALTER TABLE `chat_notes`
  ADD CONSTRAINT `chat_notes_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `chat_notes_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  ADD CONSTRAINT `chat_notes_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Constraints for table `encoder_data`
--
ALTER TABLE `encoder_data`
  ADD CONSTRAINT `encoder_data_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `loadcell_data`
--
ALTER TABLE `loadcell_data`
  ADD CONSTRAINT `loadcell_data_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `sessions` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `patients`
--
ALTER TABLE `patients`
  ADD CONSTRAINT `patients_ibfk_1` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`) ON DELETE SET NULL;

--
-- Constraints for table `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  ADD CONSTRAINT `sessions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
