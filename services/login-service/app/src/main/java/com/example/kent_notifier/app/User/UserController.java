package com.example.kent_notifier.app.User;

import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.example.kent_notifier.app.User.Model.User;
import com.example.kent_notifier.app.User.Repository.*;
import com.example.kent_notifier.app.Security.JWT.JwtUtils;

import com.example.kent_notifier.app.User.DTO.LoginRequestDTO;
import com.example.kent_notifier.app.User.DTO.LoginResponseDTO;
import com.example.kent_notifier.app.User.DTO.SignupRequestDTO;

import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("login-service/auth")
public class UserController {
    
    private final UserRepository userRepository;
    
    private final UserService userService;

    private final AuthenticationManager authenticationManager;

    private final JwtUtils jwtUtils;
    
    @Autowired
    public UserController(UserRepository userRepository, UserService userService, AuthenticationManager authenticationManager, JwtUtils jwtUtils) {
        this.userRepository = userRepository;
        this.userService = userService;
        this.authenticationManager = authenticationManager;
        this.jwtUtils = jwtUtils;
    }

    @PostMapping("/v1/signup")
    public ResponseEntity<Map<String, String>> signUp(@RequestBody SignupRequestDTO signupRequestDTO) {

        User user = userService.createUser(signupRequestDTO);
        userRepository.save(user);

        // Use a hashmap to return the message
        Map<String, String> response = new HashMap<>();
        response.put("message", "user registered successfully!");

        return ResponseEntity.ok(response);
    }

    @PostMapping("/v1/signin")
    public ResponseEntity<LoginResponseDTO> signIn(@RequestBody LoginRequestDTO loginRequestDTO) {
        Authentication authentication = authenticationManager
        .authenticate(new UsernamePasswordAuthenticationToken(loginRequestDTO.getEmail(), loginRequestDTO.getPassword()));
       
        String jwt = jwtUtils.generateJwtToken(authentication);

        LoginResponseDTO response = new LoginResponseDTO();
        
        // Set the response
        response.setToken(jwt);
        response.setExpirationTime(jwtUtils.getExpirationTimeFromJwt(jwt).getTime());
        response.setEmail(loginRequestDTO.getEmail());
        
        return ResponseEntity.ok(response);
    }
}
