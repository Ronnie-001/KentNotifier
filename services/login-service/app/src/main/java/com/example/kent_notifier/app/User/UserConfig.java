package com.example.kent_notifier.app.User;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import com.example.kent_notifier.app.User.Repository.RoleRepository;
import com.example.kent_notifier.app.User.Repository.UserRepository;

@Configuration
public class UserConfig {
    
    @Bean
    CustomUserDetailsService customUserDetailsService(UserRepository userRepository) {
        return new CustomUserDetailsService(userRepository);
    }
    
    @Bean
    UserService userService(RoleRepository roleRepository, UserMapper userMapper) {
        return new UserService(roleRepository, userMapper);
    }
}
