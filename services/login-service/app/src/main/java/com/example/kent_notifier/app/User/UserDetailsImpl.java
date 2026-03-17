package com.example.kent_notifier.app.User;

import com.example.kent_notifier.app.Role.Model.Role;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import java.util.List;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Set;

public class UserDetailsImpl implements UserDetails {

    // Define role prefix for user authorities
    private final String ROLE_PREFIX = "ROLE_";
    
    // fields of user.
    private Long id;

    private String email;

    private String password;
    
    private Set<Role> roles;

    public UserDetailsImpl(String email, String password, Set<Role> roles) {
        this.email = email;
        this.password = password;
        this.roles = roles;
    }
    
    public String getEmail() {
        return this.email;
    }

    @Override
    public String getPassword() {
        return this.password;
    }

    public Set<Role> getRoles() {
        return this.roles;
    }

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        List<GrantedAuthority> list = new ArrayList<>();

        for (Role role : this.getRoles()) {
            list.add(new SimpleGrantedAuthority(ROLE_PREFIX + role.getRoleName()));
        }

        return list;
    }
   
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    @Override
    public boolean isAccountNonLocked() {
        return true;
    }
    
    @Override
    public boolean isEnabled() {
        return true;
    }

    @Override
    public String getUsername() {
        return null;
    } 
}
