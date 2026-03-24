package com.example.kent_notifier.app.User.DTO;

import lombok.Data;

@Data
public class LoginResponseDTO {

    private String token;

    private Long expirationTime;

    private String email;
}
