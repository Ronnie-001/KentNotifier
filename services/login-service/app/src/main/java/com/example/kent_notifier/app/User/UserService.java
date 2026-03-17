package com.example.kent_notifier.app.User;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashSet;

import com.example.kent_notifier.app.User.Model.*;
import com.example.kent_notifier.app.User.DTO.*;
import com.example.kent_notifier.app.User.Repository.*;

import com.example.kent_notifier.app.Role.Model.Role;
import com.example.kent_notifier.app.Role.ERole;

@Service
public class UserService {

    private final RoleRepository roleRepository;

    private final UserMapper userMapper;

    @Autowired
    public UserService(RoleRepository roleRepository, UserMapper userMapper) {
        this.roleRepository = roleRepository;
        this.userMapper = userMapper;
    }

    public User createUser(SignupRequestDTO signupRequestDTO) {
        User user = userMapper.toEntity(signupRequestDTO);

        // search role repository to find roles
        Role role = roleRepository.findByName(ERole.USER)
                    .orElseThrow(() -> new RuntimeException("ERROR: Role not found.")); 


        HashSet<Role> roles = new HashSet<>();
        roles.add(role);

        user.setRoles(roles); 
        return user; 
    }
}



